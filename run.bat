@echo off
title IA Local Offline - Inicializador
cls

echo ===================================================
echo     IA LOCAL 100%% OFFLINE - SISTEMA DE CHAT E RAG
echo ===================================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 goto NOPYTHON

echo [2/4] Verificando ambiente virtual .venv...
if not exist ".venv" python -m venv .venv

set PY_EXE=.venv\Scripts\python.exe
if not exist "%PY_EXE%" set PY_EXE=python

echo [3/4] Verificando dependencias...
"%PY_EXE%" -m pip install -q -r requirements.txt

echo [4/4] Verificando servico Ollama...
"%PY_EXE%" -c "import httpx, subprocess, os; pass" >nul 2>&1

echo.
echo ===================================================
echo   Servidor iniciado em: http://localhost:8000
echo   Abrindo navegador automaticamente...
echo ===================================================
echo.

start http://localhost:8000

"%PY_EXE%" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
goto END

:NOPYTHON
echo [ERRO] Python nao foi encontrado no sistema!
echo Por favor, instale o Python 3.10 ou superior.
pause

:END
pause
