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
        
        # Tabela de Pastas / Projetos (v8.0)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de Conversas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                folder_id TEXT DEFAULT '',
                system_prompt TEXT DEFAULT '',
                model TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migração segura para adicionar folder_id se a tabela já existia
        try:
            cursor.execute("ALTER TABLE conversations ADD COLUMN folder_id TEXT DEFAULT ''")
        except Exception:
            pass

        # Tabela de Mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT DEFAULT '[]',
                is_favorite INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
            )
        """)

        # Migração segura para adicionar is_favorite se a tabela já existia
        try:
            cursor.execute("ALTER TABLE messages ADD COLUMN is_favorite INTEGER DEFAULT 0")
        except Exception:
            pass

        # Tabela de Documentos
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
        
        # Tabela de Memória de Longo Prazo Auto-Evolutiva (v5.0)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_memories (
                id TEXT PRIMARY KEY,
                category TEXT DEFAULT 'Preferência',
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

# --- PASTAS / PROJETOS (v8.0) ---
def create_folder(name: str) -> Dict[str, Any]:
    folder_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO folders (id, name, created_at) VALUES (?, ?, ?)", (folder_id, name, now))
        conn.commit()
    return {"id": folder_id, "name": name, "created_at": now}

def list_folders() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM folders ORDER BY name ASC")
        return [dict(r) for r in cursor.fetchall()]

def delete_folder(folder_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE conversations SET folder_id = '' WHERE folder_id = ?", (folder_id,))
        cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
        conn.commit()

# --- CONVERSAS ---
def create_conversation(title: str = "Nova Conversa", system_prompt: str = "", model: str = "", folder_id: str = "") -> Dict[str, Any]:
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (id, title, folder_id, system_prompt, model, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (conv_id, title, folder_id, system_prompt, model, now, now)
        )
        conn.commit()
    return {"id": conv_id, "title": title, "folder_id": folder_id, "system_prompt": system_prompt, "model": model, "created_at": now, "updated_at": now}

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

def update_conversation(conv_id: str, title: Optional[str] = None, system_prompt: Optional[str] = None, model: Optional[str] = None, folder_id: Optional[str] = None):
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
    if folder_id is not None:
        fields.append("folder_id = ?")
        values.append(folder_id)
        
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

# --- MENSAGENS & FAVORITOS (v8.0) ---
def add_message(conv_id: str, role: str, content: str, sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    msg_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    sources_json = json.dumps(sources or [])
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (id, conversation_id, role, content, sources, is_favorite, timestamp) VALUES (?, ?, ?, ?, ?, 0, ?)",
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
        "is_favorite": 0,
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

def toggle_favorite_message(msg_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_favorite FROM messages WHERE id = ?", (msg_id,))
        row = cursor.fetchone()
        if not row:
            return False
        new_val = 0 if row["is_favorite"] else 1
        cursor.execute("UPDATE messages SET is_favorite = ? WHERE id = ?", (new_val, msg_id))
        conn.commit()
        return bool(new_val)

def get_favorite_messages() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT m.*, c.title as conversation_title FROM messages m JOIN conversations c ON m.conversation_id = c.id WHERE m.is_favorite = 1 ORDER BY m.timestamp DESC")
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

def search_messages_content(query: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        q = f"%{query}%"
        cursor.execute("SELECT m.*, c.title as conversation_title FROM messages m JOIN conversations c ON m.conversation_id = c.id WHERE m.content LIKE ? ORDER BY m.timestamp DESC LIMIT 20", (q,))
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

# --- DOCUMENTOS RAG ---
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

# --- MEMÓRIA DE LONGO PRAZO ---
def add_memory(memory_key: str, memory_value: str, category: str = "Preferência") -> Dict[str, Any]:
    mem_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_memories (id, category, memory_key, memory_value, created_at) VALUES (?, ?, ?, ?, ?)",
            (mem_id, category, memory_key, memory_value, now)
        )
        conn.commit()
    return {"id": mem_id, "category": category, "memory_key": memory_key, "memory_value": memory_value, "created_at": now}

def get_all_memories() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_memories ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]

def delete_memory(memory_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_memories WHERE id = ?", (memory_id,))
        conn.commit()
