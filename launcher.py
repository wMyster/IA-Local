import os
import sys
import time
import threading
import webbrowser
import subprocess
import httpx
import uvicorn
from PIL import Image, ImageDraw

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

def create_tray_icon():
    try:
        import pystray
        
        # Gerar um ícone de 64x64 com degradê roxo/azul para a bandeja do Windows
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=(99, 102, 241, 255), outline=(168, 85, 247, 255), width=3)
        draw.ellipse((20, 20, 44, 44), fill=(255, 255, 255, 255))
        
        def on_open_browser(icon, item):
            webbrowser.open("http://localhost:8000")
            
        def on_check_status(icon, item):
            webbrowser.open("http://localhost:8000/api/status")

        def on_exit(icon, item):
            print("[INFO] Encerrando IA Local...")
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("🌐 Abrir Interface Web", on_open_browser, default=True),
            pystray.MenuItem("⚡ Status do Servidor", on_check_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌ Sair da IA Local", on_exit)
        )
        
        icon = pystray.Icon("IALocal", image, "IA Universal v4.0 - Ativo na Porta 8000", menu)
        # Executar loop de eventos de interface na Thread Principal
        icon.run()
    except Exception as e:
        print(f"[AVISO] Ícone da bandeja indisponível: {e}")
        # Se pystray falhar por falta de GUI, mantém o processo ativo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            os._exit(0)

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
            print("[OK] Comando de inicialização do Ollama enviado.")
            time.sleep(3)
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar Ollama: {e}")

def open_browser():
    time.sleep(1.8)
    webbrowser.open("http://localhost:8000")

def main_launcher():
    print("===================================================")
    print("  INICIANDO IA UNIVERSAL v4.0 PARA TODOS")
    print("===================================================")
    print("Servidor web em: http://localhost:8000")
    
    db.init_db()
    
    # 1. Garantir que Ollama está ativo
    threading.Thread(target=ensure_ollama_running, daemon=True).start()

    # 2. Abrir navegador automaticamente
    threading.Thread(target=open_browser, daemon=True).start()

    # 3. Iniciar Uvicorn FastAPI em thread daemon
    server_thread = threading.Thread(
        target=uvicorn.run,
        args=(main.app,),
        kwargs={"host": "127.0.0.1", "port": 8000, "log_level": "error"},
        daemon=True
    )
    server_thread.start()

    # 4. Iniciar ícone da bandeja na THREAD PRINCIPAL (evita crash do Win32 event loop)
    create_tray_icon()

if __name__ == "__main__":
    main_launcher()
