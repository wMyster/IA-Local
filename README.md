# 🧠 IA Universal v6.0 (Ultimate Edition) - IA Local, Arena & Diagramas

Uma plataforma moderna de Inteligência Artificial **100% Gratuita, de Código Aberto e 100% Offline** (com opção de **Live Web Scraper em Tempo Real**). 

Desenvolvida em **Python (FastAPI)** com interface web estilo Glassmorphism, busca semântica em documentos (RAG), suporte à visão por imagem, pré-visualização de código ao vivo, entrada por voz (microfone), **Modo Equipe de IAs (Multi-Agent)**, **Memória Auto-Evolutiva de Longo Prazo**, **Arena de Comparação de 2 Modelos Lado a Lado** e **Diagramas Mermaid.js ao vivo**. Empacotada em um **arquivo executável `.exe` único e portátil para Windows**.

---

## 🌟 Recursos Exclusivos da Versão 6.0 (Ultimate Edition)

- ⚔️ **Arena de Comparação de Modelos Lado a Lado**: Compare 2 IAs ao vivo na mesma tela dividida em 2 colunas com velocidade e respostas em tempo real.
- 📊 **Renderizador de Diagramas Mermaid.js ao Vivo**: A IA gera fluxogramas, diagramas de sequência e mapas mentais renderizados graficamente na conversa.
- ⚡ **Central de Templates de Prompts Rápidos**: Prompts de 1 clique para Landing Pages HTML/CSS, Auditoria de Código, Flashcards de Estudo e E-mails Corporativos.
- 🎭 **Modo Equipe de IAs (Multi-Agent Workflow)**: 3 Agentes Especialistas (Pesquisador ➔ Criador ➔ Revisor) colaborando em cadeia.
- 🧠 **Memória de Longo Prazo Auto-Evolutiva**: A IA aprende seu perfil, regras e preferências e guarda no banco SQLite para todas as futuras conversas.
- 🎤 **Entrada por Voz (Speech-to-Text)**: Fale suas perguntas pelo microfone com transcrição em tempo real (`Alt + M`).
- 📑 **Abas de Chat Simultâneas**: Navegue entre múltiplos chats abertos em paralelo no topo da tela.
- ⚡ **Resumo de PDFs em 1 Clique & Leitor Lado a Lado**: Resuma documentos instantaneamente e leia todo o texto extraído em um painel lateral (`👁️`).
- 📦 **Executável Único Portátil (`IALocal.exe`)**: Empacotado em um único arquivo sem pastas externas. Não requer Python instalado no computador de destino.
- 🌐 **Live Web Scraper em Tempo Real**: Busca na internet, abre assincronamente as páginas dos 3 melhores resultados, extrai o conteúdo e responde com citações e links clicáveis.
- 👁️ **Análise de Imagens (Visão Multimodal)**: Upload e análise de fotos (`.png`, `.jpg`, `.webp`) usando modelos como `llava` e `llama3.2-vision`.

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

## 📄 Licença

Este projeto é de código aberto sob a licença **MIT**.
