import os
import sys
import time
import threading
import webbrowser
import subprocess
import httpx
import uvicorn

# Suporte a PyInstaller --onefile (sys._MEIPASS) e --onedir
if getattr(sys, 'frozen', False):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    os.chdir(base_dir)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

import database as db
import main

OLLAMA_URL = "http://localhost:11434"

def ensure_ollama_running():
    try:
        resp = httpx.get(f"{OLLAMA_URL}/api/version", timeout=2.0)
        if resp.status_code == 200:
            print("[OK] Serviço Ollama ativo.")
            return
    except Exception:
        pass

    print("[AVISO] Ollama não detectado. Tentando iniciar em segundo plano...")
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    ollama_path = os.path.join(local_app_data, "Programs", "Ollama", "ollama.exe")
    
    if os.path.exists(ollama_path):
        try:
            subprocess.Popen([ollama_path, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[OK] Ollama iniciado.")
            time.sleep(3)
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar Ollama: {e}")

def start_server():
    uvicorn.run(main.app, host="0.0.0.0", port=8000, log_level="error")

def main_entry():
    print("===================================================")
    print("     IA LOCAL 100% OFFLINE v2.0 - SINGLE .EXE")
    print("===================================================")
    
    db.init_db()
    ensure_ollama_running()
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    print("[OK] Servidor ativo em http://localhost:8000")
    print("[OK] Abrindo navegador...")
    
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando...")

if __name__ == "__main__":
    main_entry()
