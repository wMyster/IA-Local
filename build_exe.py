import subprocess
import os
import sys
import shutil

def build():
    print("===================================================")
    print("   GERANDO SINGLE EXECUTABLE (.EXE ÚNICO)")
    print("===================================================")
    
    # Limpar pastas dist e build anteriores se existirem
    if os.path.exists("dist"):
        shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=IALocal",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--add-data=static;static",
        "launcher.py"
    ]
    
    print(f"Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    exe_path = os.path.abspath("dist/IALocal.exe")
    if result.returncode == 0 and os.path.exists(exe_path):
        print("\n===================================================")
        print(" SUCCESS! Arquivo .EXE único gerado em:")
        print(f" {exe_path}")
        print("===================================================")
    else:
        print("\n[ERRO] Falha na compilação do executável único.")

if __name__ == "__main__":
    build()
