from fastapi import FastAPI, Header, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pathlib import Path
from datetime import datetime, timezone
from typing import Literal
import json, os, hmac
from .sync_store import append_event, list_events, principal_for_token, create_invite, join_network, login_network, list_members, add_message, list_messages, add_observation, list_observations, revoke_session

app = FastAPI(title='PREPPER MAP API', version='2.5.0', description='API de sincronización e inteligencia territorial con control de acceso y trazabilidad.')
origins = [x.strip() for x in os.getenv('CORS_ORIGINS', 'http://localhost:8080,tauri://localhost,http://tauri.localhost,https://tauri.localhost').split(',') if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=['GET','POST'], allow_headers=['Authorization','Content-Type'])
ROOT = Path(__file__).resolve().parents[2]

def read_json(path, fallback):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError): return fallback

# Configure PREPPER_TOKENS as JSON: {"long-random-token":"admin", "other-token":"operator"}.
# No default credentials are shipped. Each installation must provision secrets out of band.
def current_principal(authorization: str | None = Header(default=None)):
    raw = os.getenv('PREPPER_TOKENS', '{}')
    try: tokens = json.loads(raw)
    except json.JSONDecodeError: raise HTTPException(503, 'PREPPER_TOKENS no contiene JSON válido.')
    if not isinstance(tokens, dict) or not tokens:
        raise HTTPException(503, 'API de sincronización deshabilitada: no hay credenciales configuradas.')
    supplied = authorization[7:] if authorization and authorization.startswith('Bearer ') else ''
    role = None
    for token, claims in tokens.items():
        if isinstance(token, str) and hmac.compare_digest(token, supplied) and isinstance(claims, dict):
            role = claims.get('role'); tenant_id = claims.get('tenant_id'); actor = claims.get('actor', role)
    if not role:
        db_principal = principal_for_token(supplied)
        if db_principal:
            return db_principal
        raise HTTPException(401, 'Credencial no válida.')
    if role not in ('admin','operator','viewer','member') or not isinstance(tenant_id, str) or len(tenant_id) < 2: raise HTTPException(403, 'Credencial sin rol o tenant válido.')
    return {'role': role, 'actor': actor, 'tenant_id': tenant_id}

def require_roles(*roles):
    def check(principal=Depends(current_principal)):
        if principal['role'] not in roles: raise HTTPException(403, 'Permiso insuficiente.')
        return principal
    return check

class EventIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    event_id: str = Field(min_length=8, max_length=100)
    entity_type: Literal['incident','resource','assignment','mutual_aid','situation_report','observation','group_message','group_observation']
    entity_id: str = Field(min_length=1, max_length=100)
    operation: Literal['create','update','delete','status_change']
    created_at: str = Field(min_length=10, max_length=40)
    source_device: str | None = Field(default=None, max_length=100)
    schema_version: int = Field(default=1, ge=1, le=10)
    payload: dict

    @field_validator('created_at')
    @classmethod
    def valid_datetime(cls, value):
        try: datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError: raise ValueError('created_at debe ser fecha ISO-8601.')
        return value

    @field_validator('payload')
    @classmethod
    def bounded_payload(cls, value):
        if len(json.dumps(value, ensure_ascii=False).encode('utf-8')) > 65536: raise ValueError('payload supera 64 KiB.')
        return value

class SyncBatch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tenant_id: str = Field(min_length=2, max_length=80)
    events: list[EventIn] = Field(min_length=1, max_length=250)

@app.get('/health')
def health():
    return {'status':'ok','version':'2.5.0','sync_auth_configured': bool(os.getenv('PREPPER_TOKENS')),
            'database':'sqlite_event_store','warning':'Health del API no certifica recursos ni operación en terreno.'}

@app.get('/api/status')
def status():
    manifest=read_json(ROOT/'gis/downloaded/manifest.json', {'items':[],'status':'not_extracted'})
    items=manifest.get('items',[])
    return {'project':'PREPPER MAP PRO','version':'2.5.0','checked_at':datetime.now(timezone.utc).isoformat(),
      'catalog_layers':sum(len(s.get('layers',[])) for s in read_json(ROOT/'gis/sources/sources.json',{}).get('sources',[])),
      'layers_downloaded':sum(x.get('status')=='downloaded' for x in items),'layers_failed':sum(x.get('status')=='failed' for x in items),
      'sync_enabled':bool(os.getenv('PREPPER_TOKENS')),'warning':'No usar este estado como alerta oficial ni confirmación de disponibilidad.'}

@app.get('/api/sources')
def sources(): return read_json(ROOT/'gis/sources/sources.json', {'sources':[]})
@app.get('/api/manifest')
def manifest(): return read_json(ROOT/'gis/downloaded/manifest.json', {'status':'not_extracted','items':[]})
@app.get('/api/layers')
def layers():
    data=read_json(ROOT/'gis/downloaded/manifest.json', {'items':[]})
    return {'items':[x for x in data.get('items',[]) if x.get('status')=='downloaded']}
@app.get('/api/places')
def places(municipality: str|None=None, category: str|None=None):
    data=read_json(ROOT/'data/reference/places.geojson', {'type':'FeatureCollection','features':[]})
    fs=data.get('features',[])
    if municipality: fs=[f for f in fs if f.get('properties',{}).get('municipality','').casefold()==municipality.casefold()]
    if category: fs=[f for f in fs if f.get('properties',{}).get('category','').casefold()==category.casefold()]
    return {'type':'FeatureCollection','features':fs}

class InviteRequest(BaseModel):
    role: Literal['member','viewer'] = 'member'
    hours: int = Field(default=72, ge=1, le=720)
    max_uses: int = Field(default=1, ge=1, le=20)

class JoinRequest(BaseModel):
    code: str = Field(min_length=6, max_length=80)
    username: str = Field(min_length=3, max_length=32, pattern=r'^[a-zA-Z0-9_.-]+$')
    display_name: str = Field(min_length=2, max_length=60)
    password: str = Field(min_length=10, max_length=128)

class LoginRequest(BaseModel):
    tenant_id: str = Field(min_length=2, max_length=80)
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=10, max_length=128)

class MessageRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

class ObservationRequest(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    body: str = Field(min_length=1, max_length=3000)
    category: Literal['general','weather','route','resource','hazard','meeting'] = 'general'
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

@app.post('/api/network/invites')
def network_create_invite(req: InviteRequest, principal=Depends(require_roles('admin','operator'))):
    return create_invite(principal['tenant_id'], principal.get('actor','admin'), req.role, req.hours, req.max_uses)

@app.post('/api/network/join')
def network_join(req: JoinRequest):
    result, error = join_network(req.code, req.username, req.display_name, req.password)
    if error: raise HTTPException(400, error)
    return result

@app.post('/api/network/login')
def network_login(req: LoginRequest):
    result = login_network(req.tenant_id, req.username, req.password)
    if not result: raise HTTPException(401, 'Usuario o contraseña incorrectos.')
    return result

@app.post('/api/network/logout')
def network_logout(authorization: str | None = Header(default=None), principal=Depends(current_principal)):
    supplied = authorization[7:] if authorization and authorization.startswith('Bearer ') else ''
    return {'revoked': revoke_session(supplied)}

@app.get('/api/network/me')
def network_me(principal=Depends(current_principal)):
    return {'user_id':principal.get('user_id'), 'tenant_id':principal['tenant_id'],
            'username':principal.get('actor'), 'display_name':principal.get('display_name',principal.get('actor')),
            'role':principal['role']}

@app.get('/api/network/members')
def network_members(principal=Depends(current_principal)):
    return {'members':list_members(principal['tenant_id'])}

@app.get('/api/network/messages')
def network_get_messages(limit: int=Query(default=100,ge=1,le=200), principal=Depends(current_principal)):
    return {'messages':list_messages(principal['tenant_id'],limit)}

@app.post('/api/network/messages')
def network_post_message(req: MessageRequest, principal=Depends(require_roles('admin','operator','member'))):
    return add_message(principal['tenant_id'], principal.get('user_id','legacy'), principal.get('display_name',principal.get('actor','integrante')), req.body.strip())

@app.get('/api/network/observations')
def network_get_observations(limit: int=Query(default=100,ge=1,le=200), principal=Depends(current_principal)):
    return {'observations':list_observations(principal['tenant_id'],limit)}

@app.post('/api/network/observations')
def network_post_observation(req: ObservationRequest, principal=Depends(require_roles('admin','operator','member'))):
    if (req.latitude is None) != (req.longitude is None):
        raise HTTPException(400, 'Para ubicar una observación debes indicar latitud y longitud.')
    return add_observation(principal['tenant_id'], principal.get('user_id','legacy'),
        principal.get('display_name',principal.get('actor','integrante')), req.title, req.body,
        req.latitude, req.longitude, req.category)

@app.post('/api/sync/push')
def sync_push(batch: SyncBatch, principal=Depends(require_roles('admin','operator','member'))):
    if batch.tenant_id != principal['tenant_id']: raise HTTPException(403, 'Tenant no autorizado para esta credencial.')
    results=[append_event(e.model_dump(), principal['actor'], batch.tenant_id) for e in batch.events]
    return {'tenant_id':batch.tenant_id,'accepted':sum(x['accepted'] for x in results),'duplicates':sum(x['duplicate'] for x in results),'results':results}

@app.get('/api/sync/pull')
def sync_pull(tenant_id: str=Query(min_length=2,max_length=80), since: str|None=None, limit: int=Query(default=500,ge=1,le=1000), principal=Depends(require_roles('admin','operator','viewer','member'))):
    if tenant_id != principal['tenant_id']: raise HTTPException(403, 'Tenant no autorizado para esta credencial.')
    events=list_events(tenant_id,since,limit)
    return {'tenant_id':tenant_id,'events':events,'count':len(events)}
