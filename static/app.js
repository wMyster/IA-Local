// ESTADO GLOBAL DA APLICAÇÃO
let currentConversationId = null;
let selectedModel = "";
let currentSystemPrompt = "Você é um assistente virtual útil, preciso e atencioso.";
let isStreaming = false;
let isSpeaking = false;
let isWebSearchEnabled = false;
let currentUtterance = null;
let allConversations = [];

const PERSONAS = {
    general: "Você é um assistente virtual útil, preciso e atencioso.",
    coder: "Você é um especialista sênior em programação. Responda com código limpo, comentado e otimizado. Use blocos de código com a linguagem especificada.",
    doc_analyzer: "Você é um analista especialista em documentos. Resuma textos com clareza e extraia os pontos-chave dos arquivos anexados ao contexto."
};

// INICIALIZAÇÃO
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupMarkedOptions();
    checkOllamaStatus();
    loadAvailableModels();
    loadConversationsList();
    initTheme();
});

function setupMarkedOptions() {
    marked.setOptions({
        gfm: true,
        breaks: true,
        headerIds: false
    });
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#btn-theme-toggle i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
    }
}

// EVENT LISTENERS
function setupEventListeners() {
    document.getElementById('btn-new-chat').addEventListener('click', createNewChat);

    document.getElementById('btn-toggle-sidebar').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('collapsed');
    });

    document.getElementById('btn-theme-toggle').addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    // Toggle Pesquisa Web
    const webBtn = document.getElementById('btn-toggle-web');
    const webIndicator = document.getElementById('web-search-indicator');
    webBtn.addEventListener('click', () => {
        isWebSearchEnabled = !isWebSearchEnabled;
        webBtn.classList.toggle('active', isWebSearchEnabled);
        if (isWebSearchEnabled) {
            webIndicator.className = 'active';
            webIndicator.innerHTML = '<i class="fa-solid fa-globe"></i> 🌐 Pesquisa Web Ativada (Grátis em tempo real)';
        } else {
            webIndicator.className = 'text-muted';
            webIndicator.innerHTML = '<i class="fa-solid fa-shield-halved"></i> Modo 100% Offline e Privado';
        }
    });

    document.getElementById('history-search-input').addEventListener('input', (e) => {
        filterConversations(e.target.value);
    });

    document.getElementById('select-model').addEventListener('change', (e) => {
        selectedModel = e.target.value;
        if (currentConversationId) {
            updateConversationMeta({ model: selectedModel });
        }
    });

    document.getElementById('select-persona').addEventListener('change', (e) => {
        const val = e.target.value;
        if (val === 'custom') {
            openPromptModal();
        } else if (PERSONAS[val]) {
            currentSystemPrompt = PERSONAS[val];
            document.getElementById('modal-system-prompt').value = currentSystemPrompt;
            if (currentConversationId) {
                updateConversationMeta({ system_prompt: currentSystemPrompt });
            }
        }
    });

    document.getElementById('btn-edit-prompt').addEventListener('click', openPromptModal);
    document.getElementById('btn-close-modal').addEventListener('click', closePromptModal);
    document.getElementById('btn-save-prompt').addEventListener('click', () => {
        currentSystemPrompt = document.getElementById('modal-system-prompt').value;
        if (currentConversationId) {
            updateConversationMeta({ system_prompt: currentSystemPrompt });
        }
        closePromptModal();
    });

    document.getElementById('btn-manage-models').addEventListener('click', openModelsModal);
    document.getElementById('btn-close-models-modal').addEventListener('click', closeModelsModal);
    document.getElementById('btn-start-pull').addEventListener('click', startModelPull);

    const exportBtn = document.getElementById('btn-export-dropdown');
    const exportMenu = document.getElementById('export-menu');
    exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exportMenu.classList.toggle('hidden');
    });
    document.addEventListener('click', () => exportMenu.classList.add('hidden'));

    document.getElementById('btn-upload').addEventListener('click', () => {
        document.getElementById('file-upload-input').click();
    });
    document.getElementById('file-upload-input').addEventListener('change', handleFileUpload);

    document.getElementById('btn-send').addEventListener('click', sendMessage);
    
    const textarea = document.getElementById('chat-input');
    textarea.addEventListener('input', () => {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
    });
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    document.getElementById('btn-refresh-status').addEventListener('click', checkOllamaStatus);
}

// STATUS DO OLLAMA
async function checkOllamaStatus() {
    const card = document.getElementById('ollama-status-card');
    const text = document.getElementById('ollama-status-text');
    const detail = document.getElementById('ollama-status-detail');

    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.status === 'online') {
            card.className = 'status-card online';
            text.innerText = 'Ollama Conectado';
            detail.innerText = `v${data.version} | 100% Offline`;
        } else {
            card.className = 'status-card offline';
            text.innerText = 'Ollama Desconectado';
            detail.innerText = 'Inicie o serviço Ollama';
        }
    } catch (err) {
        card.className = 'status-card offline';
        text.innerText = 'Servidor Offline';
        detail.innerText = 'Verifique backend Python';
    }
}

// MODELOS
async function loadAvailableModels() {
    const select = document.getElementById('select-model');
    try {
        const res = await fetch('/api/models');
        const data = await res.json();
        select.innerHTML = '';

        if (data.models && data.models.length > 0) {
            data.models.forEach(modelName => {
                const opt = document.createElement('option');
                opt.value = modelName;
                opt.innerText = modelName;
                select.appendChild(opt);
            });
            selectedModel = data.models[0];
        } else {
            const opt = document.createElement('option');
            opt.value = '';
            opt.innerText = 'Nenhum modelo baixado';
            select.appendChild(opt);
        }
    } catch (err) {
        select.innerHTML = '<option value="">Erro ao carregar modelos</option>';
    }
}

// GERENCIADOR DE MODELOS
function openModelsModal() {
    document.getElementById('models-modal').classList.remove('hidden');
    renderInstalledModelsList();
}

function closeModelsModal() {
    document.getElementById('models-modal').classList.add('hidden');
}

async function renderInstalledModelsList() {
    const container = document.getElementById('installed-models-list');
    container.innerHTML = 'Carregando...';

    try {
        const res = await fetch('/api/models');
        const data = await res.json();
        container.innerHTML = '';

        if (!data.models || data.models.length === 0) {
            container.innerHTML = '<div class="text-muted">Nenhum modelo instalado.</div>';
            return;
        }

        data.models.forEach(modelName => {
            const item = document.createElement('div');
            item.className = 'installed-model-item';
            item.innerHTML = `
                <div class="model-name">
                    <i class="fa-solid fa-cube"></i> ${escapeHtml(modelName)}
                </div>
                <button class="delete-model-btn" onclick="deleteModel('${escapeHtml(modelName)}')"><i class="fa-solid fa-trash"></i></button>
            `;
            container.appendChild(item);
        });
    } catch (err) {
        container.innerHTML = 'Erro ao listar modelos.';
    }
}

async function deleteModel(modelName) {
    if (!confirm(`Deseja realmente excluir o modelo ${modelName}?`)) return;

    try {
        const res = await fetch(`/api/models/${encodeURIComponent(modelName)}`, { method: 'DELETE' });
        if (res.ok) {
            await loadAvailableModels();
            await renderInstalledModelsList();
        } else {
            alert('Falha ao excluir o modelo.');
        }
    } catch (err) {
        alert('Erro ao conectar ao servidor.');
    }
}

async function startModelPull() {
    const input = document.getElementById('pull-model-input');
    const modelName = input.value.trim();
    if (!modelName) {
        alert('Digite o nome do modelo que deseja baixar (ex: deepseek-r1:7b).');
        return;
    }

    const progressContainer = document.getElementById('pull-progress-container');
    const statusText = document.getElementById('pull-status-text');
    const percentText = document.getElementById('pull-percent-text');
    const progressBar = document.getElementById('pull-progress-bar');
    const btnPull = document.getElementById('btn-start-pull');

    progressContainer.classList.remove('hidden');
    btnPull.disabled = true;
    statusText.innerText = `Baixando ${modelName}...`;

    try {
        const response = await fetch('/api/models/pull', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_name: modelName })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const payload = JSON.parse(line.substring(6));
                        if (payload.percent !== undefined) {
                            percentText.innerText = `${payload.percent}%`;
                            progressBar.style.width = `${payload.percent}%`;
                        }
                        if (payload.status) {
                            statusText.innerText = payload.status;
                        }
                    } catch (e) {}
                }
            }
        }
        alert(`Download de ${modelName} concluído com sucesso!`);
        input.value = '';
        await loadAvailableModels();
        await renderInstalledModelsList();
    } catch (err) {
        alert(`Erro ao baixar o modelo ${modelName}.`);
    } finally {
        btnPull.disabled = false;
        progressContainer.classList.add('hidden');
    }
}

// CONVERSAS & BUSCA NO HISTÓRICO
async function loadConversationsList() {
    try {
        const res = await fetch('/api/conversations');
        allConversations = await res.json();
        renderConversations(allConversations);

        if (!currentConversationId && allConversations.length > 0) {
            loadConversation(allConversations[0].id);
        }
    } catch (err) {
        console.error('Erro ao carregar conversas:', err);
    }
}

function filterConversations(query) {
    const q = query.toLowerCase().trim();
    if (!q) {
        renderConversations(allConversations);
        return;
    }
    const filtered = allConversations.filter(c => c.title.toLowerCase().includes(q));
    renderConversations(filtered);
}

function renderConversations(conversations) {
    const container = document.getElementById('conversations-list');
    container.innerHTML = '';

    if (conversations.length === 0) {
        container.innerHTML = '<div style="padding: 10px; font-size: 12px; color: var(--text-muted);">Nenhuma conversa encontrada.</div>';
        return;
    }

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conv-item ${conv.id === currentConversationId ? 'active' : ''}`;
        item.dataset.id = conv.id;
        item.onclick = () => loadConversation(conv.id);

        item.innerHTML = `
            <div class="conv-title">
                <i class="fa-regular fa-message"></i>
                <span>${escapeHtml(conv.title)}</span>
            </div>
            <div class="conv-actions">
                <button class="conv-action-btn" onclick="deleteConv(event, '${conv.id}')" title="Excluir"><i class="fa-solid fa-trash"></i></button>
            </div>
        `;
        container.appendChild(item);
    });
}

async function createNewChat() {
    try {
        const res = await fetch('/api/conversations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: 'Nova Conversa',
                system_prompt: currentSystemPrompt,
                model: selectedModel
            })
        });
        const conv = await res.json();
        currentConversationId = conv.id;
        await loadConversationsList();
        loadConversation(conv.id);
    } catch (err) {
        console.error('Erro ao criar conversa:', err);
    }
}

async function loadConversation(convId) {
    currentConversationId = convId;
    
    document.querySelectorAll('.conv-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === convId);
    });

    try {
        const res = await fetch(`/api/conversations/${convId}`);
        const data = await res.json();
        
        document.getElementById('current-chat-title').innerText = data.conversation.title;
        if (data.conversation.system_prompt) {
            currentSystemPrompt = data.conversation.system_prompt;
            document.getElementById('modal-system-prompt').value = currentSystemPrompt;
        }

        renderMessages(data.messages);
        renderAttachedDocuments(data.documents);
    } catch (err) {
        console.error('Erro ao carregar detalhes da conversa:', err);
    }
}

async function updateConversationMeta(updates) {
    if (!currentConversationId) return;
    try {
        await fetch(`/api/conversations/${currentConversationId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
    } catch (err) {
        console.error('Erro ao atualizar metadata:', err);
    }
}

async function deleteConv(event, convId) {
    event.stopPropagation();
    if (!confirm('Deseja realmente excluir esta conversa?')) return;

    try {
        await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
        if (currentConversationId === convId) {
            currentConversationId = null;
        }
        await loadConversationsList();
    } catch (err) {
        console.error('Erro ao deletar conversa:', err);
    }
}

function exportCurrentChat(format) {
    if (!currentConversationId) return;
    window.location.href = `/api/conversations/${currentConversationId}/export?format=${format}`;
}

// UPLOAD DE DOCUMENTOS (RAG)
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file || !currentConversationId) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await fetch(`/api/conversations/${currentConversationId}/upload`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            loadConversation(currentConversationId);
        } else {
            alert('Erro ao processar o documento.');
        }
    } catch (err) {
        alert('Erro no envio do arquivo.');
    } finally {
        e.target.value = '';
    }
}

function renderAttachedDocuments(docs) {
    const bar = document.getElementById('attached-docs-bar');
    const container = document.getElementById('docs-chips-container');
    container.innerHTML = '';

    if (!docs || docs.length === 0) {
        bar.classList.add('hidden');
        return;
    }

    bar.classList.remove('hidden');
    docs.forEach(d => {
        const chip = document.createElement('div');
        chip.className = 'doc-chip';
        chip.innerHTML = `
            <i class="fa-solid fa-file-lines"></i>
            <span>${escapeHtml(d.filename)} (${d.chunk_count} trechos)</span>
            <i class="fa-solid fa-xmark doc-chip-remove" onclick="deleteDocument('${d.id}')"></i>
        `;
        container.appendChild(chip);
    });
}

async function deleteDocument(docId) {
    if (!currentConversationId) return;
    try {
        await fetch(`/api/conversations/${currentConversationId}/documents/${docId}`, { method: 'DELETE' });
        loadConversation(currentConversationId);
    } catch (err) {
        console.error('Erro ao deletar documento:', err);
    }
}

// MENSAGENS, STREAMING E FONTES
function renderMessages(messages) {
    const container = document.getElementById('messages-container');
    container.innerHTML = '';

    if (!messages || messages.length === 0) {
        const welcome = document.getElementById('welcome-screen');
        if (welcome) {
            container.appendChild(welcome.cloneNode(true));
        }
        return;
    }

    messages.forEach(msg => {
        appendMessageUI(msg.role, msg.content, msg.sources);
    });

    scrollToBottom();
}

function appendMessageUI(role, content, sources = [], metrics = null) {
    const container = document.getElementById('messages-container');
    
    const welcome = container.querySelector('.welcome-screen');
    if (welcome) welcome.remove();

    const row = document.createElement('div');
    row.className = `message-row ${role}`;

    const avatarIcon = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `<div class="rag-sources"><div class="sources-title"><i class="fa-solid fa-bookmark"></i> Fontes & Contexto Consultados:</div>`;
        sources.forEach(s => {
            if (s.type === 'web') {
                sourcesHtml += `<a class="source-badge" href="${escapeHtml(s.url)}" target="_blank" title="${escapeHtml(s.url)}"><i class="fa-solid fa-globe"></i> Web: ${escapeHtml(s.title)}</a>`;
            } else {
                sourcesHtml += `<span class="source-badge" title="Relevância: ${Math.round((s.score || 0) * 100)}%"><i class="fa-solid fa-file-text"></i> Doc: ${escapeHtml(s.filename)} (Trecho ${(s.chunk_index || 0) + 1})</span>`;
            }
        });
        sourcesHtml += `</div>`;
    }

    let toolbarHtml = '';
    if (role === 'assistant') {
        const metricsStr = metrics ? `⚡ ${metrics.tokens_per_second} t/s (${metrics.elapsed_seconds}s, ${metrics.tokens} tokens)` : '⚡ Resposta instantânea';
        toolbarHtml = `
            <div class="message-footer-toolbar">
                <span class="metrics-badge">${metricsStr}</span>
                <button class="speech-btn" onclick="toggleSpeech(this)" title="Ouvir resposta por voz"><i class="fa-solid fa-volume-high"></i> Ouvir</button>
            </div>
        `;
    }

    row.innerHTML = `
        <div class="avatar">${avatarIcon}</div>
        <div class="message-bubble">
            <div class="message-text">${role === 'user' ? escapeHtml(content) : marked.parse(content)}</div>
            ${sourcesHtml}
            ${toolbarHtml}
        </div>
    `;

    container.appendChild(row);
    formatCodeBlocks(row);
    scrollToBottom();
    return row;
}

async function sendMessage() {
    if (isStreaming) return;

    const input = document.getElementById('chat-input');
    const prompt = input.value.trim();
    if (!prompt || !currentConversationId) return;

    if (!selectedModel) {
        alert('Por favor, selecione um modelo de IA no topo da tela antes de enviar.');
        return;
    }

    input.value = '';
    input.style.height = 'auto';

    appendMessageUI('user', prompt);

    const assistantRow = appendMessageUI('assistant', '');
    const textElement = assistantRow.querySelector('.message-text');
    textElement.classList.add('cursor-typing');

    isStreaming = true;
    let fullReply = '';
    let sources = [];
    let metrics = null;

    try {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                prompt: prompt,
                model: selectedModel,
                system_prompt: currentSystemPrompt,
                web_search: isWebSearchEnabled
            })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const payload = JSON.parse(line.substring(6));
                        
                        if (payload.type === 'sources') {
                            sources = payload.sources;
                        } else if (payload.type === 'token') {
                            fullReply += payload.content;
                            textElement.innerHTML = marked.parse(fullReply);
                            formatCodeBlocks(assistantRow);
                            scrollToBottom();
                        } else if (payload.type === 'metrics') {
                            metrics = payload.metrics;
                            const badge = assistantRow.querySelector('.metrics-badge');
                            if (badge && metrics) {
                                badge.innerText = `⚡ ${metrics.tokens_per_second} t/s (${metrics.elapsed_seconds}s, ${metrics.tokens} tokens)`;
                            }
                        } else if (payload.type === 'title_update') {
                            document.getElementById('current-chat-title').innerText = payload.title;
                            loadConversationsList();
                        }
                    } catch (e) {
                        console.error('Erro ao ler linha SSE:', e);
                    }
                }
            }
        }
    } catch (err) {
        fullReply += '\n\n⚠️ Erro de conexão durante a comunicação com a IA.';
        textElement.innerHTML = marked.parse(fullReply);
    } finally {
        textElement.classList.remove('cursor-typing');
        isStreaming = false;
        loadConversationsList();
    }
}

// LEITOR POR VOZ
function toggleSpeech(btn) {
    if (!('speechSynthesis' in window)) {
        alert('Seu navegador não suporta leitura por voz.');
        return;
    }

    if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Ouvir';
        return;
    }

    const bubble = btn.closest('.message-bubble');
    const text = bubble.querySelector('.message-text').innerText;

    currentUtterance = new SpeechSynthesisUtterance(text);
    currentUtterance.lang = 'pt-BR';
    currentUtterance.rate = 1.0;

    currentUtterance.onend = () => {
        isSpeaking = false;
        btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Ouvir';
    };

    window.speechSynthesis.speak(currentUtterance);
    isSpeaking = true;
    btn.innerHTML = '<i class="fa-solid fa-square"></i> Parar';
}

function formatCodeBlocks(container) {
    container.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
        
        const parent = block.parentElement;
        if (!parent.querySelector('.copy-code-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-code-btn';
            copyBtn.innerText = 'Copiar';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(block.innerText);
                copyBtn.innerText = 'Copiado!';
                setTimeout(() => copyBtn.innerText = 'Copiar', 2000);
            };
            parent.appendChild(copyBtn);
        }
    });
}

function setInputPrompt(text) {
    const input = document.getElementById('chat-input');
    input.value = text;
    input.focus();
}

function scrollToBottom() {
    const viewport = document.querySelector('.chat-viewport');
    viewport.scrollTop = viewport.scrollHeight;
}

function openPromptModal() {
    document.getElementById('prompt-modal').classList.remove('hidden');
    document.getElementById('modal-system-prompt').value = currentSystemPrompt;
}

function closePromptModal() {
    document.getElementById('prompt-modal').classList.add('hidden');
}

function escapeHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}
