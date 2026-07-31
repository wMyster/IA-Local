import os
import sys
import time
import socket
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

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_available_port(start_port: int = 8000) -> int:
    for port in range(start_port, start_port + 50):
        if not is_port_in_use(port):
            return port
    return start_port

def is_our_app_running(port: int = 8000) -> bool:
    try:
        resp = httpx.get(f"http://localhost:{port}/api/status", timeout=1.0)
        if resp.status_code == 200:
            return True
    except Exception:
        pass
    return False

def create_tray_icon(port: int):
    try:
        import pystray
        
        image = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=(99, 102, 241, 255), outline=(168, 85, 247, 255), width=3)
        draw.ellipse((20, 20, 44, 44), fill=(255, 255, 255, 255))
        
        def on_open_browser(icon, item):
            webbrowser.open(f"http://localhost:{port}")
            
        def on_check_status(icon, item):
            webbrowser.open(f"http://localhost:{port}/api/status")

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
        
        icon = pystray.Icon("IALocal", image, f"IA Universal - Porta {port}", menu)
        icon.run()
    except Exception as e:
        print(f"[AVISO] Ícone da bandeja indisponível: {e}")
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

def open_browser(port: int):
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{port}")

def main_launcher():
    print("===================================================")
    print("  INICIANDO IA UNIVERSAL v4.0 PARA TODOS")
    print("===================================================")
    
    # 1. Se a nossa aplicação já estiver rodando na porta 8000, apenas abre o navegador
    if is_our_app_running(8000):
        print("[INFO] IA Local já está rodando na porta 8000! Abrindo o navegador...")
        webbrowser.open("http://localhost:8000")
        return

    # 2. Selecionar uma porta livre disponível (8000, 8001, 8002...)
    port = find_available_port(8000)
    print(f"Servidor web ativo na porta: http://localhost:{port}")
    
    db.init_db()
    
    # 3. Garantir que Ollama está ativo em segundo plano
    threading.Thread(target=ensure_ollama_running, daemon=True).start()

    # 4. Abrir navegador na porta atribuída
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    # 5. Iniciar Uvicorn na porta selecionada
    server_thread = threading.Thread(
        target=uvicorn.run,
        args=(main.app,),
        kwargs={"host": "127.0.0.1", "port": port, "log_level": "error"},
        daemon=True
    )
    server_thread.start()

    # 6. Iniciar ícone da bandeja do Windows na Thread Principal
    create_tray_icon(port)

if __name__ == "__main__":
    main_launcher()
