import uvicorn
import webbrowser
import sys
import os
import threading
import time
from app.main import app

def start_server():
    """Inicia o servidor Uvicorn"""
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

def start_browser():
    """Abre o navegador em modo Aplicativo (sem barra de URL)"""
    time.sleep(2)
    url = "http://localhost:8000"
    
    # Tenta encontrar Edge ou Chrome para abrir como App
    import subprocess
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    try:
        if os.path.exists(edge_path):
            subprocess.Popen([edge_path, f"--app={url}"])
            print("Abrindo com Edge em modo App")
        elif os.path.exists(chrome_path):
            subprocess.Popen([chrome_path, f"--app={url}"])
            print("Abrindo com Chrome em modo App")
        else:
            # Fallback para navegador padrao
            webbrowser.open(url)
    except Exception as e:
        print(f"Erro ao abrir navegador: {e}")
        webbrowser.open(url)

if __name__ == "__main__":
    # Inicia o servidor em uma thread separada
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Abre o navegador
    start_browser()
    
    # Mantém o script rodando
    print("Sistema CalibraCore Lab rodando em modo Desktop.")
    print("Para acessar de outro PC na rede, use o IP desta máquina na porta 8000.")
    print("Feche esta janela para encerrar o servidor.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando...")
        sys.exit(0)
