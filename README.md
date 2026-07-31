# 🧠 IA Universal v7.0 (Masterpiece Edition) - IA Local, Hardware & Slides

Uma plataforma moderna de Inteligência Artificial **100% Gratuita, de Código Aberto e 100% Offline** (com opção de **Live Web Scraper em Tempo Real**). 

Desenvolvida em **Python (FastAPI)** com interface web estilo Glassmorphism, busca semântica em documentos (RAG), suporte à visão por imagem, pré-visualização de código ao vivo, entrada por voz (microfone), **Modo Equipe de IAs (Multi-Agent)**, **Memória Auto-Evolutiva de Longo Prazo**, **Arena de Comparação de 2 Modelos**, **Diagramas Mermaid.js ao vivo**, **Criador de Slides HTML5** e **Monitor de Recursos de Hardware do PC em Tempo Real**. Empacotada em um **arquivo executável `.exe` único e portátil para Windows**.

---

## 🌟 Recursos de Alto Nível da Versão 7.0 (Masterpiece Edition)

- 📊 **Monitor de Recursos de Hardware em Tempo Real**: Medidor de consumo de CPU (%) e Memória RAM (GB e %) exibido ao vivo no rodapé da Sidebar.
- 🎬 **Criador de Apresentações de Slides HTML5**: Geração de apresentações estilo PowerPoint/Reveal.js com preview interativo e navegação por setas (`←` e `→`).
- ⚔️ **Arena de Comparação de Modelos Lado a Lado**: Compare 2 IAs ao vivo na mesma tela dividida em 2 colunas com velocidade em tempo real.
- 📊 **Renderizador de Diagramas Mermaid.js ao Vivo**: Geração gráfica instantânea de fluxogramas e mapas mentais.
- ⚡ **Central de Templates de Prompts Rápidos**: Prompts de 1 clique para Landing Pages, Slides HTML5, Auditoria de Código e Flashcards de Estudo.
- 🎭 **Modo Equipe de IAs (Multi-Agent Workflow)**: 3 Agentes Especialistas (Pesquisador ➔ Criador ➔ Revisor) colaborando em cadeia.
- 🧠 **Memória de Longo Prazo Auto-Evolutiva**: A IA aprende seu perfil, regras e preferências e guarda no banco SQLite para todas as futuras conversas.
- 🎤 **Entrada por Voz (Speech-to-Text)**: Fale suas perguntas pelo microfone com transcrição em tempo real (`Alt + M`).
- 📦 **Executável Único Portátil (`IALocal.exe`)**: Empacotado em um único arquivo sem pastas externas. Não requer Python instalado no computador de destino.

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
