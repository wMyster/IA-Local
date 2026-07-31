# 🧠 IA Local Gratuita 100% Offline (Chat + RAG + Ollama)

Uma aplicação de Inteligência Artificial completa, gratuita e **100% offline** que roda diretamente no seu computador com privacidade total. Seus dados e documentos **nunca saem da sua máquina**.

---

## 🌟 Funcionalidades Principais

- ⚡ **Respostas em Tempo Real (Token-a-Token)**: Respostas estilo ChatGPT fluídas via SSE (Server-Sent Events).
- 🔒 **100% Offline e Gratuito**: Sem chaves de API pagas, sem envio de dados para servidores externos.
- 📄 **RAG para Documentos (Busca Semântica)**: Faça upload de arquivos `.pdf`, `.txt`, `.md` ou `.docx` e converse diretamente sobre o conteúdo deles.
- 🗃️ **Histórico Local em SQLite**: Crie, altere a persona, renomeie e exclua conversas salvos automaticamente.
- 🤖 **Seletor de Modelos Dinâmico**: Detecta automaticamente os modelos instalados no seu Ollama (ex: `llama3.2`, `qwen2.5`, `deepseek-r1`, `mistral`, `phi4`).
- 🎨 **Interface Web Moderna Premium**: Design Glassmorphism, temas Dark/Light, formatação Markdown e destaque de sintaxe em código com botão de copiar.
- 🎭 **Personas & System Prompts Customizáveis**: Escolha perfis prontos (Assistente Geral, Especialista em Código, Analista de Documentos) ou crie suas próprias instruções.

---

## 🚀 Como Instalar e Rodar

### Passo 1: Instalar o Ollama (Motor de IA Local)

1. Baixe e instale o Ollama gratuitamente no site oficial: **[https://ollama.com](https://ollama.com)**
2. Abra o terminal (CMD ou PowerShell) e baixe um ou mais modelos de sua preferência. Sugestões de modelos leves e potentes:
   ```bash
   # Modelo leve e muito rápido (Meta Llama 3.2 3B)
   ollama pull llama3.2

   # Modelo excelente em Português e Código (Qwen 2.5 7B ou 3B)
   ollama pull qwen2.5

   # Modelo de Raciocínio Avançado
   ollama pull deepseek-r1:1.5b
   ```

---

### Passo 2: Iniciar a Aplicação

#### Opção A: No Windows (1-Click Startup)
Basta dar dois cliques no arquivo **`run.bat`** (ou executar **`.\run.ps1`** no PowerShell).

O script irá:
1. Criar o ambiente virtual Python (`.venv`) automaticamente.
2. Instalar todas as dependências do `requirements.txt`.
3. Verificar a conexão com o serviço Ollama.
4. Iniciar o servidor e abrir **`http://localhost:8000`** no seu navegador padrão.

---

#### Opção B: Inicialização Manual (Qualquer Sistema Operacional)

1. **Criar e ativar ambiente virtual Python**:
   ```bash
   python -m venv .venv
   
   # No Windows (CMD / PowerShell):
   .venv\Scripts\activate
   
   # No Linux / macOS:
   source .venv/bin/activate
   ```

2. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar o Servidor FastAPI**:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

4. Acesse no seu navegador: **`http://localhost:8000`**

---

## 💻 Estrutura do Projeto

```
.
├── main.py              # Servidor FastAPI com streaming SSE e rotas da API
├── database.py          # Gerenciamento do banco de dados SQLite local (local_ai.db)
├── rag_engine.py        # Extração de texto de PDF/DOCX, chunking e TF-IDF RAG
├── requirements.txt     # Dependências Python (fastapi, uvicorn, pypdf, etc.)
├── run.bat              # Script de inicialização automática (CMD Windows)
├── run.ps1              # Script de inicialização automática (PowerShell)
├── README.md            # Documentação do projeto
└── static/
    ├── index.html       # Interface Web HTML5 moderna
    ├── styles.css       # Design System Glassmorphism com temas Dark/Light
    └── app.js           # Lógica JavaScript (Stream SSE, Markdown, RAG e UI)
```

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3, FastAPI, Uvicorn, SQLite.
- **RAG & NLP**: PyPDF, python-docx, Scikit-learn (TF-IDF & Cosine Similarity).
- **Inference Engine**: Ollama API REST (`http://localhost:11434`).
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript ES6, Marked.js, Highlight.js, FontAwesome.
