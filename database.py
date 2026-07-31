import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = "local_ai.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabela de Conversas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                system_prompt TEXT DEFAULT '',
                model TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de Mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT DEFAULT '[]',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        """)
        
        # Tabela de Documentos anexados ao Chat
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                chunk_count INTEGER DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def create_conversation(title: str = "Nova Conversa", system_prompt: str = "", model: str = "") -> Dict[str, Any]:
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, title, system_prompt, model, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (conv_id, title, system_prompt, model, now, now)
        )
        conn.commit()
    return {"id": conv_id, "title": title, "system_prompt": system_prompt, "model": model, "created_at": now, "updated_at": now}

def list_conversations() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_conversation(conv_id: str, title: Optional[str] = None, system_prompt: Optional[str] = None, model: Optional[str] = None):
    now = datetime.now().isoformat()
    fields = []
    values = []
    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if system_prompt is not None:
        fields.append("system_prompt = ?")
        values.append(system_prompt)
    if model is not None:
        fields.append("model = ?")
        values.append(model)
        
    if not fields:
        return
        
    fields.append("updated_at = ?")
    values.append(now)
    values.append(conv_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE conversations SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()

def delete_conversation(conv_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        cursor.execute("DELETE FROM documents WHERE conversation_id = ?", (conv_id,))
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()

def add_message(conv_id: str, role: str, content: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    msg_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    sources_json = json.dumps(sources or [])
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, sources, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (msg_id, conv_id, role, content, sources_json, now)
        )
        cursor.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
        conn.commit()
        
    return {
        "id": msg_id,
        "conversation_id": conv_id,
        "role": role,
        "content": content,
        "sources": sources or [],
        "timestamp": now
    }

def get_messages(conv_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conv_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            item = dict(r)
            try:
                item["sources"] = json.loads(item.get("sources", "[]"))
            except Exception:
                item["sources"] = []
            result.append(item)
        return result

def add_document_record(conv_id: str, filename: str, file_type: str, chunk_count: int) -> Dict[str, Any]:
    doc_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (id, conversation_id, filename, file_type, chunk_count, uploaded_at) VALUES (?, ?, ?, ?, ?, ?)",
            (doc_id, conv_id, filename, file_type, chunk_count, now)
        )
        conn.commit()
    return {"id": doc_id, "conversation_id": conv_id, "filename": filename, "file_type": file_type, "chunk_count": chunk_count, "uploaded_at": now}

def get_documents(conv_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE conversation_id = ? ORDER BY uploaded_at DESC", (conv_id,))
        return [dict(r) for r in cursor.fetchall()]

def delete_document_record(doc_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
