from adjudication.audit.event_store import EventStore


def test_hash_chain_persists_and_detects_tampering(tmp_path):
    path = tmp_path / "audit.db"
    store = EventStore(path)
    assert store.verify()
    first = store.append("SYN-A", "SYN-C", {"action": "created"})
    second = store.append("SYN-B", "SYN-C", {"action": "created"})
    assert first != second and store.verify()
    store.close()
    store = EventStore(path)
    assert len(store.all()) == 2 and store.verify()
    with store.db:
        store.db.execute("UPDATE events SET body='tampered' WHERE seq=1")
    assert not store.verify()
    store.close()
