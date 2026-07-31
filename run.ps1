# Script de Inicialização PowerShell - IA Local 100% Offline
$Host.UI.RawUI.WindowTitle = "IA Local Offline"

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "    IA LOCAL 100% OFFLINE - SISTEMA DE CHAT & RAG" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/4] Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python não foi encontrado no sistema!" -ForegroundColor Red
    Write-Host "Por favor, instale o Python 3.10 ou superior." -ForegroundColor Yellow
    Exit 1
}

# 2. Criar Venv se não existir
if (-not (Test-Path ".venv")) {
    Write-Host "[2/4] Criando ambiente virtual .venv..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[2/4] Ambiente virtual .venv já existe." -ForegroundColor Green
}

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
}

# 3. Instalar dependências
Write-Host "[3/4] Instalando / Atualizando dependências..." -ForegroundColor Yellow
& $venvPython -m pip install -q -r requirements.txt

# 4. Verificar Ollama
Write-Host "[4/4] Testando conexão com Ollama (http://localhost:11434)..." -ForegroundColor Yellow
try {
    $ollamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -TimeoutSec 3
    Write-Host "[OK] Ollama ativo (Versão: $($ollamaCheck.version))" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Ollama não está ativo na porta 11434!" -ForegroundColor Red
    Write-Host "Para usar a IA, abra o Ollama ou execute no terminal: ollama run llama3.2 ou ollama run qwen2.5" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   Servidor rodando em: http://localhost:8000" -ForegroundColor Green
Write-Host "   Abrindo o navegador..." -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:8000"

& $venvPython -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
