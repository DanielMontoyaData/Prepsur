import json
from backend.app import sync_store

def test_event_store_is_idempotent_and_tenant_scoped(tmp_path, monkeypatch):
    monkeypatch.setattr(sync_store, 'DB_PATH', tmp_path/'sync.sqlite3')
    event={'event_id':'event-000001','entity_type':'incident','entity_id':'INC-1','operation':'create','created_at':'2026-11-17T10:00:00Z','payload':{'priority':'P2'}}
    first=sync_store.append_event(event,'operator-1','tenant-a')
    second=sync_store.append_event(event,'operator-1','tenant-a')
    assert first['accepted'] is True and second['duplicate'] is True
    assert len(sync_store.list_events('tenant-a')) == 1
    assert sync_store.list_events('tenant-b') == []
    row=sync_store.list_events('tenant-a')[0]
    assert len(row['payload_sha256']) == 64
    assert row['payload']['priority']=='P2'
