# 🧠 IA Universal v4.0 (Super Edition) - IA Local, Visão & Live Web Scraper

Uma plataforma moderna de Inteligência Artificial **100% Gratuita, de Código Aberto e 100% Offline** (com opção de **Live Web Scraper em Tempo Real**). 

Desenvolvida em **Python (FastAPI)** com interface web estilo Glassmorphism, busca semântica em documentos (RAG), suporte à visão por imagem, pré-visualização de código ao vivo, entrada por voz (microfone) e empacotada em um **arquivo executável `.exe` único e portátil para Windows**.

---

## 🌟 Principais Recursos da Versão 4.0

- 🎤 **Entrada por Voz (Speech-to-Text)**: Fale suas perguntas pelo microfone com transcrição em tempo real (`Alt + M`).
- 📑 **Abas de Chat Simultâneas**: Navegue entre múltiplos chats abertos em paralelo no topo da tela.
- ⚡ **Resumo de PDFs em 1 Clique & Leitor Lado a Lado**: Resuma documentos instantaneamente e leia todo o texto extraído em um painel lateral (`👁️`).
- ⌨️ **Atalhos de Teclado**: `Ctrl+N` (Novo Chat), `Ctrl+K` (Foco na Busca), `Alt+M` (Microfone), `Esc` (Fechar Modais).
- 📦 **Executável Único Portátil (`IALocal.exe`)**: Empacotado em um único arquivo sem pastas externas. Não requer Python instalado no computador de destino.
- 🌐 **Live Web Scraper em Tempo Real**: Quando ativado, a IA busca na internet, abre assincronamente as páginas dos 3 melhores resultados, extrai o conteúdo atualizado e responde com citações e links clicáveis.
- 👁️ **Análise de Imagens (Visão Multimodal)**: Suporte a upload e análise de fotos (`.png`, `.jpg`, `.webp`) usando modelos como `llava` e `llama3.2-vision`.
- 👁️ **Live Code Preview (Execução ao Vivo)**: Ao solicitar códigos em HTML5, CSS3 ou JavaScript, a IA exibe o botão **"👁️ Ver Preview"** para você testar a página web ao vivo no próprio aplicativo.
- ⚙️ **Painel de Hiperparâmetros da IA**: Ajuste dinâmico de **Temperatura**, **Janela de Contexto (`num_ctx` de 2048 a 16384 tokens)** e **Top-P**.
- 📄 **RAG em Documentos Locais**: Envie arquivos PDF, TXT ou DOCX para realizar pesquisas semânticas.
- 🔔 **Bandeja do Sistema Windows (System Tray)**: Exibe um ícone permanente ao lado do relógio do Windows com menu interativo.
- 🛑 **Botão Parar Resposta**: Interrompa a geração da IA em tempo real a qualquer momento via `AbortController`.

---

## 📁 Estrutura do Projeto

```text
├── launcher.py         # Inicializador silencioso com suporte ao System Tray do Windows
├── main.py             # Servidor web FastAPI com streaming SSE, Visão, RAG e Leitor de Docs
├── web_search.py       # Módulo de busca na web e Live Web Scraper de páginas
├── database.py         # Camada de persistência local SQLite (local_ai.db)
├── rag_engine.py       # Leitor de PDF/TXT/DOCX e busca semântica por similaridade
├── build_exe.py        # Script de compilação PyInstaller para gerar executável único
├── build.bat           # Script batch para compilar o dist/IALocal.exe com 1 clique
├── run.bat / run.ps1   # Scripts de execução rápida em ambiente de desenvolvimento
├── requirements.txt    # Dependências do projeto Python
└── static/
    ├── index.html      # Interface Web (Abas, Microfone, Modais)
    ├── styles.css      # Design System Glassmorphism, temas e responsividade
    └── app.js          # Lógica da aplicação (Voice Recognition, Multi-tabs, Live Preview)
```

---

## 🚀 Como Executar

### Opção 1: Executável `.exe` Portátil (Recomendado para Usuários)

1. Baixe o arquivo **`dist/IALocal.exe`**.
2. Dê dois cliques em **`IALocal.exe`**.
3. O servidor será iniciado em segundo plano, o ícone reaparecerá na bandeja do Windows (próximo ao relógio) e o seu navegador padrão abrirá automaticamente em `http://localhost:8000`.

### Opção 2: Pelo Código-Fonte (Desenvolvedores)

```bash
git clone https://github.com/wMyster/IA-Local.git
cd IA-Local
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python launcher.py
```

---

## 🤖 Modelos Recomendados (Via Ollama)

| Modelo | Tamanho | Recomendação |
| :--- | :--- | :--- |
| `qwen2.5:3b` | 1.9 GB | Modelo ultra-rápido e preciso para programação e conversação. |
| `llama3.2:3b` | 2.0 GB | Excelente para raciocínio geral e tarefas do dia a dia. |
| `deepseek-r1:7b` | 4.7 GB | Raciocínio lógico avançado e resolução de problemas complexos. |
| `gemma2:2b` | 1.6 GB | Leve, super veloz para CPUs simples. |
| `llava:7b` | 4.5 GB | **Visão Multimodal**: Análise de imagens, fotos e prints. |

---

## 📄 Licença

Este projeto é de código aberto sob a licença **MIT**.
