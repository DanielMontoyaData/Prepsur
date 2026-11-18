"""SQLite append-only event inbox/outbox with idempotency and audit metadata."""
from __future__ import annotations
import json, os, sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(os.getenv('PREPPER_SYNC_DB', Path(__file__).resolve().parents[2] / 'data' / 'sync.sqlite3'))

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS events (
      event_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, entity_type TEXT NOT NULL,
      entity_id TEXT NOT NULL, operation TEXT NOT NULL, payload_json TEXT NOT NULL,
      created_at TEXT NOT NULL, received_at TEXT NOT NULL, actor TEXT NOT NULL,
      source_device TEXT, schema_version INTEGER NOT NULL DEFAULT 1,
      payload_sha256 TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_events_tenant_received ON events(tenant_id, received_at);
    CREATE INDEX IF NOT EXISTS idx_events_entity ON events(tenant_id, entity_type, entity_id);
    CREATE TABLE IF NOT EXISTS audit (
      audit_id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL,
      action TEXT NOT NULL, actor TEXT NOT NULL, occurred_at TEXT NOT NULL,
      result TEXT NOT NULL, detail TEXT
    );
    CREATE TABLE IF NOT EXISTS network_users (
      user_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, username TEXT NOT NULL,
      display_name TEXT NOT NULL, password_salt TEXT NOT NULL, password_hash TEXT NOT NULL,
      token_hash TEXT NOT NULL UNIQUE, role TEXT NOT NULL DEFAULT 'member',
      created_at TEXT NOT NULL, last_seen TEXT
    );
    CREATE UNIQUE INDEX IF NOT EXISTS idx_network_username ON network_users(tenant_id, username);
    CREATE TABLE IF NOT EXISTS network_sessions (
      token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, created_at TEXT NOT NULL,
      revoked_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_network_sessions_user ON network_sessions(user_id);
    CREATE TABLE IF NOT EXISTS network_invites (
      invite_hash TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, created_by TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'member', expires_at TEXT NOT NULL,
      max_uses INTEGER NOT NULL DEFAULT 1, uses INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS network_messages (
      message_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, user_id TEXT NOT NULL,
      display_name TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_network_messages ON network_messages(tenant_id, created_at);
    CREATE TABLE IF NOT EXISTS network_observations (
      observation_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, user_id TEXT NOT NULL,
      display_name TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
      latitude REAL, longitude REAL, category TEXT NOT NULL DEFAULT 'general',
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_network_observations ON network_observations(tenant_id, created_at);
    ''')
    return db

def append_event(event: dict, actor: str, tenant_id: str):
    import hashlib
    payload = json.dumps(event['payload'], ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()
    db = connect()
    try:
        cur = db.execute('''INSERT OR IGNORE INTO events
          (event_id,tenant_id,entity_type,entity_id,operation,payload_json,created_at,received_at,actor,source_device,schema_version,payload_sha256)
          VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
          (event['event_id'], tenant_id, event['entity_type'], event['entity_id'], event['operation'], payload,
           event['created_at'], now, actor, event.get('source_device'), event.get('schema_version', 1), digest))
        inserted = cur.rowcount == 1
        db.execute('INSERT INTO audit(event_id,action,actor,occurred_at,result,detail) VALUES(?,?,?,?,?,?)',
                   (event['event_id'], 'event_ingest', actor, now, 'inserted' if inserted else 'duplicate_ignored', None))
        db.commit()
        return {'event_id': event['event_id'], 'accepted': inserted, 'duplicate': not inserted, 'received_at': now}
    finally:
        db.close()

def list_events(tenant_id: str, since: str | None = None, limit: int = 500):
    db = connect()
    try:
        sql = 'SELECT * FROM events WHERE tenant_id=?'
        args = [tenant_id]
        if since:
            sql += ' AND received_at>?'; args.append(since)
        sql += ' ORDER BY received_at ASC LIMIT ?'; args.append(limit)
        rows = db.execute(sql, args).fetchall()
        return [dict(r) | {'payload': json.loads(r['payload_json'])} for r in rows]
    finally: db.close()


# Private friends network: credentials are stored as hashes, never in plaintext.
def _now():
    return datetime.now(timezone.utc).isoformat()

def create_invite(tenant_id: str, actor: str, role: str = "member", hours: int = 72, max_uses: int = 1):
    import hashlib, secrets
    code = secrets.token_urlsafe(9)
    digest = hashlib.sha256(code.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    from datetime import timedelta
    expires = (now + timedelta(hours=hours)).isoformat()
    db = connect()
    try:
        db.execute("INSERT INTO network_invites(invite_hash,tenant_id,created_by,role,expires_at,max_uses,uses,created_at) VALUES(?,?,?,?,?,?,0,?)",
                   (digest, tenant_id, actor, role, expires, max_uses, now.isoformat()))
        db.commit()
        return {"code": code, "tenant_id": tenant_id, "role": role, "expires_at": expires, "max_uses": max_uses}
    finally: db.close()

def join_network(code: str, username: str, display_name: str, password: str):
    import hashlib, secrets, uuid
    digest = hashlib.sha256(code.encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()
    db = connect()
    try:
        invite = db.execute("SELECT * FROM network_invites WHERE invite_hash=?", (digest,)).fetchone()
        if not invite: return None, "Invitación inválida."
        if invite["expires_at"] < now: return None, "La invitación venció."
        if invite["uses"] >= invite["max_uses"]: return None, "La invitación ya fue utilizada."
        tenant = invite["tenant_id"]
        if db.execute("SELECT 1 FROM network_users WHERE tenant_id=? AND username=?", (tenant, username.lower())).fetchone():
            return None, "Ese usuario ya existe en la red."
        salt = secrets.token_hex(16)
        phash = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 240000).hex()
        token = secrets.token_urlsafe(32)
        user_id = str(uuid.uuid4())
        db.execute("INSERT INTO network_users(user_id,tenant_id,username,display_name,password_salt,password_hash,token_hash,role,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                   (user_id, tenant, username.lower(), display_name, salt, phash, hashlib.sha256(token.encode()).hexdigest(), invite["role"], now))
        db.execute("INSERT INTO network_sessions(token_hash,user_id,created_at) VALUES(?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user_id, now))
        db.execute("UPDATE network_invites SET uses=uses+1 WHERE invite_hash=?", (digest,))
        db.commit()
        return {"access_token": token, "token_type": "bearer", "profile": {"user_id": user_id, "username": username.lower(), "display_name": display_name, "role": invite["role"], "tenant_id": tenant}}, None
    except Exception:
        db.rollback()
        raise
    finally: db.close()

def login_network(tenant_id: str, username: str, password: str):
    import hashlib, secrets
    db = connect()
    try:
        user = db.execute("SELECT * FROM network_users WHERE tenant_id=? AND username=?", (tenant_id, username.lower())).fetchone()
        if not user: return None
        check = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(user["password_salt"]), 240000).hex()
        if not secrets.compare_digest(check, user["password_hash"]): return None
        token = secrets.token_urlsafe(32)
        db.execute("INSERT INTO network_sessions(token_hash,user_id,created_at) VALUES(?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user["user_id"], _now()))
        db.execute("UPDATE network_users SET last_seen=? WHERE user_id=?", (_now(), user["user_id"]))
        db.commit()
        return {"access_token": token, "token_type": "bearer", "profile": {"user_id": user["user_id"], "username": user["username"], "display_name": user["display_name"], "role": user["role"], "tenant_id": tenant_id}}
    finally: db.close()

def principal_for_token(token: str):
    import hashlib
    if not token: return None
    digest = hashlib.sha256(token.encode()).hexdigest()
    db = connect()
    try:
        row = db.execute("SELECT u.user_id,u.tenant_id,u.username,u.display_name,u.role FROM network_sessions s JOIN network_users u ON u.user_id=s.user_id WHERE s.token_hash=? AND s.revoked_at IS NULL", (digest,)).fetchone()
        if not row: return None
        db.execute("UPDATE network_users SET last_seen=? WHERE user_id=?", (_now(), row["user_id"]))
        db.commit()
        return {"user_id": row["user_id"], "tenant_id": row["tenant_id"], "actor": row["username"], "display_name": row["display_name"], "role": row["role"]}
    finally: db.close()

def list_members(tenant_id: str):
    db=connect()
    try:
        rows=db.execute("SELECT user_id,username,display_name,role,created_at,last_seen FROM network_users WHERE tenant_id=? ORDER BY created_at", (tenant_id,)).fetchall()
        return [dict(r) for r in rows]
    finally: db.close()

def add_message(tenant_id: str, user_id: str, display_name: str, body: str):
    import uuid
    mid=str(uuid.uuid4()); now=_now()
    db=connect()
    try:
        db.execute("INSERT INTO network_messages VALUES(?,?,?,?,?,?)",(mid,tenant_id,user_id,display_name,body,now)); db.commit()
        return {"message_id":mid,"display_name":display_name,"body":body,"created_at":now}
    finally: db.close()

def list_messages(tenant_id: str, limit: int=100):
    db=connect()
    try:
        rows=db.execute("SELECT message_id,display_name,body,created_at FROM network_messages WHERE tenant_id=? ORDER BY created_at DESC LIMIT ?",(tenant_id,limit)).fetchall()
        return [dict(r) for r in reversed(rows)]
    finally: db.close()

def add_observation(tenant_id: str, user_id: str, display_name: str, title: str, body: str, latitude=None, longitude=None, category="general"):
    import uuid
    oid=str(uuid.uuid4()); now=_now()
    db=connect()
    try:
        db.execute("INSERT INTO network_observations VALUES(?,?,?,?,?,?,?,?,?,?)",(oid,tenant_id,user_id,display_name,title,body,latitude,longitude,category,now)); db.commit()
        return {"observation_id":oid,"display_name":display_name,"title":title,"body":body,"latitude":latitude,"longitude":longitude,"category":category,"created_at":now}
    finally: db.close()

def list_observations(tenant_id: str, limit: int=100):
    db=connect()
    try:
        rows=db.execute("SELECT observation_id,display_name,title,body,latitude,longitude,category,created_at FROM network_observations WHERE tenant_id=? ORDER BY created_at DESC LIMIT ?",(tenant_id,limit)).fetchall()
        return [dict(r) for r in rows]
    finally: db.close()


def revoke_session(token: str):
    import hashlib
    digest=hashlib.sha256(token.encode()).hexdigest()
    db=connect()
    try:
        cur=db.execute("UPDATE network_sessions SET revoked_at=? WHERE token_hash=? AND revoked_at IS NULL",(_now(),digest))
        db.commit()
        return cur.rowcount > 0
    finally: db.close()
