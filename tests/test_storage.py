def test_storage_sqlite(tmp_path):
    from storage import Storage

    db = tmp_path / "chat.db"
    store = Storage(str(db))
    store.save("Agent1", "user", "hello")
    rows = list(store.conn.execute("SELECT agent, role, content FROM messages"))
    assert rows == [("Agent1", "user", "hello")]

