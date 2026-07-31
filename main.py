import json
import time
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fpdf import FPDF

import database as db
import rag_engine as rag
import web_search

OLLAMA_URL = "http://localhost:11434"

app = FastAPI(title="IA Universal v4.0 (Super Edition)", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.init_db()

# Models de requisição
class ConversationCreate(BaseModel):
    title: Optional[str] = "Nova Conversa"
    system_prompt: Optional[str] = "Você é um assistente virtual útil, preciso e atencioso."
    model: Optional[str] = ""

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: str
    prompt: str
    model: str
    system_prompt: Optional[str] = None
    web_search: Optional[bool] = False
    images: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None

class PullModelRequest(BaseModel):
    model_name: str

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/status")
async def get_status():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/version")
            if resp.status_code == 200:
                data = resp.json()
                return {"status": "online", "version": data.get("version", "desconhecida"), "url": OLLAMA_URL}
    except Exception:
        pass
    return {"status": "offline", "version": None, "url": OLLAMA_URL}

@app.get("/api/models")
async def list_models():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"models": models, "ollama_online": True}
    except Exception as e:
        print(f"Erro ao obter modelos do Ollama: {e}")
        
    return {
        "models": ["deepseek-r1:7b", "qwen2.5:7b", "llama3.2:3b", "qwen2.5:3b", "gemma2:2b", "llava:7b"],
        "ollama_online": False
    }

@app.post("/api/models/pull")
async def pull_model(request: PullModelRequest):
    model_name = request.model_name.strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="Nome do modelo é obrigatório.")

    async def event_generator():
        try:
            async with httpx.AsyncClient(timeout=3600.0) as client:
                async with client.stream("POST", f"{OLLAMA_URL}/api/pull", json={"name": model_name, "stream": True}) as response:
                    if response.status_code != 200:
                        yield f"data: {json.dumps({'status': 'error', 'message': f'Erro no Ollama ({response.status_code})'})}\n\n"
                    else:
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    data = json.loads(line)
                                    completed = data.get("completed", 0)
                                    total = data.get("total", 0)
                                    percent = round((completed / total) * 100, 1) if total > 0 else 0
                                    status_str = data.get("status", "")
                                    
                                    yield f"data: {json.dumps({'status': status_str, 'percent': percent, 'completed': completed, 'total': total})}\n\n"
                                except Exception:
                                    pass
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
            
        yield f"data: {json.dumps({'status': 'done', 'percent': 100})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.delete("/api/models/{model_name}")
async def delete_model(model_name: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request("DELETE", f"{OLLAMA_URL}/api/delete", json={"name": model_name})
            if resp.status_code == 200:
                return {"status": "success", "message": f"Modelo {model_name} excluído."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "error", "message": "Falha ao excluir modelo."}

# CRUD de Conversas
@app.get("/api/conversations")
def get_conversations():
    return db.list_conversations()

@app.post("/api/conversations")
def create_new_conversation(data: ConversationCreate):
    return db.create_conversation(title=data.title, system_prompt=data.system_prompt, model=data.model)

@app.get("/api/conversations/{conv_id}")
def get_conversation_detail(conv_id: str):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    messages = db.get_messages(conv_id)
    documents = db.get_documents(conv_id)
    return {"conversation": conv, "messages": messages, "documents": documents}

@app.put("/api/conversations/{conv_id}")
def update_conversation(conv_id: str, data: ConversationUpdate):
    db.update_conversation(conv_id, title=data.title, system_prompt=data.system_prompt, model=data.model)
    return db.get_conversation(conv_id)

@app.delete("/api/conversations/{conv_id}")
def delete_conversation(conv_id: str):
    rag.clear_conversation_chunks(conv_id)
    db.delete_conversation(conv_id)
    return {"status": "success"}

# Exportação de Conversas (PDF, MD, JSON)
@app.get("/api/conversations/{conv_id}/export")
def export_conversation(conv_id: str, format: str = Query("md")):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    messages = db.get_messages(conv_id)
    
    title = conv.get("title", "Conversa")
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip()
    
    if format == "json":
        data_str = json.dumps({"conversation": conv, "messages": messages}, indent=2, ensure_ascii=False)
        return Response(content=data_str, media_type="application/json", headers={"Content-Disposition": f'attachment; filename="{safe_title}.json"'})
        
    elif format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Conversa: {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 8, f"Criado em: {conv.get('created_at', '')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        for msg in messages:
            role_title = "USUARIO" if msg["role"] == "user" else "ASSISTENTE (IA)"
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 8, f"[{role_title}]", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            clean_content = msg["content"].encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 6, clean_content)
            pdf.ln(4)
            
        pdf_bytes = pdf.output()
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{safe_title}.pdf"'})
        
    else:  # md (default)
        md_text = f"# Conversa: {title}\n*Criado em: {conv.get('created_at', '')}*\n\n---\n\n"
        for msg in messages:
            role_name = "👤 **Usuário**" if msg["role"] == "user" else "🤖 **Assistente IA**"
            md_text += f"### {role_name}\n\n{msg['content']}\n\n---\n\n"
        return Response(content=md_text, media_type="text/markdown", headers={"Content-Disposition": f'attachment; filename="{safe_title}.md"'})

# RAG / Documentos
@app.post("/api/conversations/{conv_id}/upload")
async def upload_document(conv_id: str, file: UploadFile = File(...)):
    conv = db.get_conversation(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
        
    file_bytes = await file.read()
    filename = file.filename
    file_type = filename.split('.')[-1].lower() if '.' in filename else 'txt'
    
    doc_id = str(db.uuid.uuid4())
    chunk_count = rag.index_document(conv_id, doc_id, filename, file_bytes)
    
    doc_record = db.add_document_record(conv_id, filename, file_type, chunk_count)
    return doc_record

@app.get("/api/conversations/{conv_id}/documents")
def get_attached_documents(conv_id: str):
    return db.get_documents(conv_id)

@app.get("/api/conversations/{conv_id}/documents/{doc_id}/text")
def get_attached_document_text(conv_id: str, doc_id: str):
    text = rag.get_document_full_text(conv_id, doc_id)
    return {"text": text}

@app.delete("/api/conversations/{conv_id}/documents/{doc_id}")
def delete_attached_document(conv_id: str, doc_id: str):
    rag.remove_document_chunks(conv_id, doc_id)
    db.delete_document_record(doc_id)
    return {"status": "success"}

# Chat Streaming SSE com RAG, Live Web Scraper, Visão Multimodal e Parâmetros
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    conv_id = request.conversation_id
    prompt = request.prompt.strip()
    model = request.model.strip()
    
    if not prompt and not request.images:
        raise HTTPException(status_code=400, detail="O prompt ou imagem é obrigatório.")
        
    db.add_message(conv_id, role="user", content=prompt)

    conv = db.get_conversation(conv_id)
    sys_prompt = request.system_prompt or (conv["system_prompt"] if conv else "")
    
    # 1. RAG de Documentos
    relevant_chunks = rag.search_relevant_chunks(conv_id, prompt, top_k=4)
    sources = []
    context_str = ""
    
    if relevant_chunks:
        context_str += "\n\n=== CONTEXTO RELEVANTE DOS DOCUMENTOS ANEXADOS ===\n"
        for i, chunk in enumerate(relevant_chunks, 1):
            sources.append({
                "type": "document",
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"]
            })
            context_str += f"--- Documento [{chunk['filename']}] (Trecho {i}) ---\n{chunk['text']}\n\n"

    # 2. Pesquisa Web e Live Web Scraper (tempo real)
    web_sources = []
    if request.web_search and prompt:
        search_results = web_search.search_web(prompt, max_results=3, deep_scrape=True)
        if search_results:
            context_str += "\n\n=== CONTEÚDO EXTRAÍDO DA INTERNET EM TEMPO REAL ===\n"
            for item in search_results:
                web_sources.append({"type": "web", "title": item["title"], "url": item["url"]})
                context_str += f"Fonte: {item['title']} ({item['url']}):\n{item['full_text']}\n\n"
            context_str += "=== FIM DO CONTEÚDO DA WEB ===\n"

    all_sources = sources + web_sources

    final_prompt = prompt
    if context_str:
        final_prompt = f"{context_str}\nPergunta do Usuário: {prompt}"

    async def event_generator():
        yield f"data: {json.dumps({'type': 'sources', 'sources': all_sources})}\n\n"
        
        full_assistant_reply = ""
        start_time = time.time()
        token_count = 0
        
        try:
            payload = {
                "model": model,
                "prompt": final_prompt,
                "stream": True
            }
            if sys_prompt:
                payload["system"] = sys_prompt
            if request.images:
                payload["images"] = request.images
            if request.options:
                payload["options"] = request.options

            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as response:
                    if response.status_code != 200:
                        err_msg = f"Erro no Ollama ({response.status_code}). Verifique se o modelo '{model}' está instalado."
                        yield f"data: {json.dumps({'type': 'token', 'content': err_msg})}\n\n"
                        full_assistant_reply += err_msg
                    else:
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    chunk_data = json.loads(line)
                                    token = chunk_data.get("response", "")
                                    if token:
                                        full_assistant_reply += token
                                        token_count += 1
                                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                                    if chunk_data.get("done", False):
                                        break
                                except Exception:
                                    pass
        except httpx.ConnectError:
            err_msg = "\n\n⚠️ **Ollama não respondeu.** Certifique-se de que o serviço está ativo ou abra o app Ollama."
            yield f"data: {json.dumps({'type': 'token', 'content': err_msg})}\n\n"
            full_assistant_reply += err_msg
        except Exception as e:
            err_msg = f"\n\nErro na geração: {str(e)}"
            yield f"data: {json.dumps({'type': 'token', 'content': err_msg})}\n\n"
            full_assistant_reply += err_msg

        elapsed_time = round(time.time() - start_time, 2)
        tokens_per_sec = round(token_count / elapsed_time, 1) if elapsed_time > 0 else 0
        
        metrics = {
            "elapsed_seconds": elapsed_time,
            "tokens": token_count,
            "tokens_per_second": tokens_per_sec
        }
        yield f"data: {json.dumps({'type': 'metrics', 'metrics': metrics})}\n\n"
            
        db.add_message(conv_id, role="assistant", content=full_assistant_reply, sources=all_sources)
        
        all_msgs = db.get_messages(conv_id)
        if len(all_msgs) <= 2 and prompt:
            auto_title = prompt[:35] + ("..." if len(prompt) > 35 else "")
            db.update_conversation(conv_id, title=auto_title)
            yield f"data: {json.dumps({'type': 'title_update', 'title': auto_title})}\n\n"
            
        yield f"data: {json.dumps({'type': 'done', 'full_content': full_assistant_reply})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
