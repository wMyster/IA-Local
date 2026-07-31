@echo off
title IA Local - Compilador EXE
cls

echo ===================================================
echo     GERANDO EXECUTAVEL PORTATIL (IALocal.exe)
echo ===================================================
echo.

set PY_EXE=.venv\Scripts\python.exe
if not exist "%PY_EXE%" set PY_EXE=python

"%PY_EXE%" build_exe.py

pause
