import os
import sqlite3

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None

class Storage:
    """Persist messages to SQLite and optionally MongoDB."""

    def __init__(self, path: str = "chat.db") -> None:
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS messages (agent TEXT, role TEXT, content TEXT)"
        )
        self.conn.commit()
        mongo_uri = os.getenv("MONGODB_URI")
        if mongo_uri and MongoClient is not None:
            self.mongo_client = MongoClient(mongo_uri)
            db_name = os.getenv("MONGODB_DB", "chat")
            self.mongo_db = self.mongo_client[db_name]
        else:
            self.mongo_client = None
            self.mongo_db = None

    def save(self, agent: str, role: str, content: str) -> None:
        self.conn.execute(
            "INSERT INTO messages (agent, role, content) VALUES (?, ?, ?)",
            (agent, role, content),
        )
        self.conn.commit()
        if self.mongo_db is not None:
            self.mongo_db.messages.insert_one(
                {"agent": agent, "role": role, "content": content}
            )

def get_storage() -> "Storage | None":
    if os.getenv("CHAT_PERSIST") or os.getenv("MONGODB_URI"):
        path = os.getenv("CHAT_DB", "chat.db")
        return Storage(path)
    return None

storage = get_storage()
