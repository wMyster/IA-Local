import io
import re
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Armazenamento em memória dos chunks indexados por conversation_id
# Estrutura: { conversation_id: [ {"doc_id": ..., "filename": ..., "chunk_index": ..., "text": ...} ] }
CONVERSATION_CHUNKS: Dict[str, List[Dict[str, Any]]] = {}

def extract_text_from_bytes(filename: str, file_bytes: bytes) -> str:
    ext = filename.lower().split('.')[-1]
    text = ""
    
    if ext == 'pdf':
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        text = "\n".join(pages_text)
        
    elif ext in ['docx', 'doc']:
        doc = docx.Document(io.BytesIO(file_bytes))
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        text = "\n".join(full_text)
        
    else:  # txt, md, csv, etc.
        try:
            text = file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            text = file_bytes.decode('latin-1', errors='ignore')
            
    # Limpeza básica de espaços excessivos
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    if not text:
        return []
        
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) + 1 <= chunk_size:
            current_chunk += ("\n" if current_chunk else "") + p
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(p) > chunk_size:
                start = 0
                while start < len(p):
                    end = start + chunk_size
                    chunks.append(p[start:end])
                    start += chunk_size - overlap
                current_chunk = ""
            else:
                current_chunk = p
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def index_document(conversation_id: str, doc_id: str, filename: str, file_bytes: bytes) -> int:
    text = extract_text_from_bytes(filename, file_bytes)
    if not text:
        return 0
        
    chunks = chunk_text(text)
    if conversation_id not in CONVERSATION_CHUNKS:
        CONVERSATION_CHUNKS[conversation_id] = []
        
    for i, c in enumerate(chunks):
        CONVERSATION_CHUNKS[conversation_id].append({
            "doc_id": doc_id,
            "filename": filename,
            "chunk_index": i,
            "text": c
        })
        
    return len(chunks)

def get_document_full_text(conversation_id: str, doc_id: str) -> str:
    chunks = CONVERSATION_CHUNKS.get(conversation_id, [])
    doc_chunks = [c["text"] for c in chunks if c.get("doc_id") == doc_id]
    return "\n\n".join(doc_chunks)

def remove_document_chunks(conversation_id: str, doc_id: str):
    if conversation_id in CONVERSATION_CHUNKS:
        CONVERSATION_CHUNKS[conversation_id] = [
            c for c in CONVERSATION_CHUNKS[conversation_id] if c["doc_id"] != doc_id
        ]

def clear_conversation_chunks(conversation_id: str):
    if conversation_id in CONVERSATION_CHUNKS:
        del CONVERSATION_CHUNKS[conversation_id]

def search_relevant_chunks(conversation_id: str, query: str, top_k: int = 4, min_score: float = 0.1) -> List[Dict[str, Any]]:
    chunks = CONVERSATION_CHUNKS.get(conversation_id, [])
    if not chunks:
        return []
        
    corpus = [c["text"] for c in chunks]
    if not corpus:
        return []
        
    try:
        vectorizer = TfidfVectorizer(stop_words=None, max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(corpus + [query])
        
        doc_vectors = tfidf_matrix[:-1]
        query_vector = tfidf_matrix[-1]
        
        similarities = cosine_similarity(query_vector, doc_vectors)[0]
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score:
                item = chunks[idx].copy()
                item["score"] = round(score, 4)
                results.append(item)
                
        return results
    except Exception as e:
        print(f"Erro na busca RAG: {e}")
        return []
