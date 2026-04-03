"""SQLite database service for conversation persistence."""

import aiosqlite
import json
import os
import uuid
from datetime import datetime
from config import get_settings


DB_PATH = None
_db_initialized = False


def _get_db_path():
    global DB_PATH
    if DB_PATH is None:
        settings = get_settings()
        DB_PATH = settings.database_path
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH


async def init_db():
    """Initialize database tables."""
    global _db_initialized
    if _db_initialized:
        return

    db_path = _get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                agent_type TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id)
        """)
        await db.commit()
    _db_initialized = True


async def create_conversation(title: str = "New Chat") -> dict:
    """Create a new conversation."""
    conv_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    db_path = _get_db_path()

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (conv_id, title, now, now)
        )
        await db.commit()

    return {"id": conv_id, "title": title, "created_at": now, "updated_at": now}


async def get_conversations() -> list[dict]:
    """List all conversations, newest first."""
    db_path = _get_db_path()
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_conversation(conv_id: str) -> dict | None:
    """Get a single conversation by ID."""
    db_path = _get_db_path()
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM conversations WHERE id = ?", (conv_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def update_conversation_title(conv_id: str, title: str):
    """Update conversation title."""
    now = datetime.utcnow().isoformat()
    db_path = _get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (title, now, conv_id)
        )
        await db.commit()


async def delete_conversation(conv_id: str):
    """Delete a conversation and all its messages."""
    db_path = _get_db_path()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        await db.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        await db.commit()


async def save_message(
    conversation_id: str,
    role: str,
    content: str,
    agent_type: str | None = None,
    metadata: dict | None = None
) -> dict:
    """Save a message to a conversation."""
    msg_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    meta_json = json.dumps(metadata) if metadata else None
    db_path = _get_db_path()

    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """INSERT INTO messages
               (id, conversation_id, role, content, agent_type, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (msg_id, conversation_id, role, content, agent_type, meta_json, now)
        )
        await db.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id)
        )
        await db.commit()

    return {
        "id": msg_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "agent_type": agent_type,
        "metadata": metadata,
        "created_at": now
    }


async def get_messages(conversation_id: str, limit: int = 50) -> list[dict]:
    """Get messages for a conversation."""
    db_path = _get_db_path()
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT * FROM messages
               WHERE conversation_id = ?
               ORDER BY created_at ASC
               LIMIT ?""",
            (conversation_id, limit)
        )
        rows = await cursor.fetchall()
        messages = []
        for row in rows:
            msg = dict(row)
            if msg.get("metadata"):
                msg["metadata"] = json.loads(msg["metadata"])
            messages.append(msg)
        return messages
