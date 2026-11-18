import json
import pytest
fastapi=pytest.importorskip('fastapi')
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app import sync_store

def test_sync_auth_tenant_isolation_and_idempotency(tmp_path, monkeypatch):
    monkeypatch.setattr(sync_store,'DB_PATH',tmp_path/'api.sqlite3')
    monkeypatch.setenv('PREPPER_TOKENS',json.dumps({'secret-token-123456789':{'role':'admin','tenant_id':'org-a','actor':'tester'}}))
    client=TestClient(app)
    event={'event_id':'event-api-0001','entity_type':'incident','entity_id':'I-1','operation':'create','created_at':'2026-11-17T12:00:00Z','payload':{'status':'open'}}
    assert client.post('/api/sync/push',json={'tenant_id':'org-b','events':[event]},headers={'Authorization':'Bearer secret-token-123456789'}).status_code==403
    r=client.post('/api/sync/push',json={'tenant_id':'org-a','events':[event]},headers={'Authorization':'Bearer secret-token-123456789'})
    assert r.status_code==200 and r.json()['accepted']==1
    r2=client.post('/api/sync/push',json={'tenant_id':'org-a','events':[event]},headers={'Authorization':'Bearer secret-token-123456789'})
    assert r2.json()['duplicates']==1
    assert client.get('/api/sync/pull?tenant_id=org-b',headers={'Authorization':'Bearer secret-token-123456789'}).status_code==403
