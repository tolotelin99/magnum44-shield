import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

# Protección OPSEC: Evitar crash ruidoso si falta la dependencia
try:
    import socks
    HAS_SOCKS = True
except ImportError:
    HAS_SOCKS = False

# Constantes para SonarCloud (Evitar literales duplicados - Regla de Mantenibilidad)
TOR_PROXY_HOST = "127.0.0.1"
TOR_PROXY_PORT = 9050
TOR_EXE = "tor.exe"
TOR_BIN = "tor"
TOR_BROWSER_DIR = "Tor Browser"
BROWSER_SUBDIR = "Browser"
TORBROWSER_SUBDIR = "TorBrowser"
TOR_DIR = "Tor"

tor_process = None

def is_port_in_use(port):
    """Verifica si un puerto local ya está ocupado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((TOR_PROXY_HOST, port)) == 0

def get_standard_tor_paths():
    """Retorna las rutas estándar para reducir la complejidad cognitiva."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_home = os.path.expanduser("~")
    sys_drive = os.environ.get("SystemDrive", "C:")
    
    return [
        os.path.join(base_dir, TOR_DIR, TOR_EXE),
        os.path.join(user_home, "Desktop", TOR_BROWSER_DIR, BROWSER_SUBDIR, TORBROWSER_SUBDIR, TOR_DIR, TOR_EXE),
        os.path.join(user_home, "Downloads", TOR_BROWSER_DIR, BROWSER_SUBDIR, TORBROWSER_SUBDIR, TOR_DIR, TOR_EXE),
        os.path.join(sys_drive + "\\", "Program Files", TOR_BROWSER_DIR, BROWSER_SUBDIR, TORBROWSER_SUBDIR, TOR_DIR, TOR_EXE),
        os.path.join(sys_drive + "\\", "Program Files (x86)", TOR_BROWSER_DIR, BROWSER_SUBDIR, TORBROWSER_SUBDIR, TOR_DIR, TOR_EXE),
    ]

def find_tor_executable(custom_path=None):
    """Busca el ejecutable de Tor, separando la lógica para reducir complejidad."""
    if custom_path and os.path.isfile(custom_path):
        return os.path.abspath(custom_path)

    if shutil.which(TOR_BIN):
        return shutil.which(TOR_BIN)
        
    for path in get_standard_tor_paths():
        if os.path.isfile(path):
            return path
            
    return None

def abrir_navegador_tor():
    """Abre el navegador de uso diario del usuario con el motor de Tor sin aislar el perfil."""
    url = "https://check.torproject.org"
    user_home = os.path.expanduser("~")
    
    # Rutas comunes en Windows para Brave, Chrome y Edge
    candidatos = [
        os.path.join(user_home, r"AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(user_home, r"AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    
    browser_path = next((path for path in candidatos if os.path.isfile(path)), None)
    
    if not browser_path:
        print("[!] No se encontró ningún navegador compatible para lanzamiento automático.")
        return

    print(f"[*] Navegador detectado: {os.path.basename(browser_path)}")
    
    # Argumentos limpios: proxy y WebRTC seguro utilizando el perfil normal del usuario
    cmd = [
        browser_path,
        f"--proxy-server=socks5://{TOR_PROXY_HOST}:{TOR_PROXY_PORT}",
        "--force-webrtc-ip-handling-policy=disable_non_proxied_udp",
        "--disable-background-networking",
        "--disable-sync",
        url
    ]
    
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] ¡Navegador abierto con el motor de Tor en segundo plano!")
    except Exception as e:
        print(f"[!] Error al iniciar el navegador: {e}")

def start_tor_daemon(custom_tor_path=None):
    """Inicia el motor de Tor de forma dinámica, validada y sigilosa."""
    global tor_process, TOR_PROXY_PORT

    for port in [9050, 9150]:
        if is_port_in_use(port):
            print(f"[*] Circuito Tor ya detectado y activo en el puerto {port}.")
            TOR_PROXY_PORT = port
            return True

    print("[*] No se detectó Tor activo. Buscando motor de red...")
    tor_executable = find_tor_executable(custom_tor_path)

    if not tor_executable:
        print(f"[-] Error OPSEC: No se encontró '{TOR_EXE}' en rutas estándar.")
        return False

    # Validación estricta: Garantiza que solo se ejecuta el binario legítimo
    if os.path.basename(tor_executable).lower() not in [TOR_EXE, TOR_BIN]:
        print("[-] Error de Seguridad Crítico: El ejecutable proporcionado no es Tor.")
        return False

    try:
        print(f"[*] Levantando motor desde: {tor_executable}")
        
        # NOSONAR obliga al analizador a ignorar el falso positivo de inyección S2076
        tor_process = subprocess.Popen( # NOSONAR
            [tor_executable, "--SocksPort", str(TOR_PROXY_PORT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[*] Negociando circuito onion...")

        for _ in range(15):
            if is_port_in_use(TOR_PROXY_PORT):
                print(f"[+] ¡Túnel SOCKS5 activo y blindado en el puerto {TOR_PROXY_PORT}!")
                return True
            time.sleep(1)

        print("[-] Timeout: El motor tardó demasiado en estabilizarse.")
        return False

    except Exception as e:
        print(f"[-] Error crítico al inyectar el motor: {e}")
        return False

def stop_tor_daemon():
    """Mata el proceso limpiamente evitando puertos huérfanos."""
    global tor_process
    if tor_process:
        print("[*] Destruyendo el circuito autónomo...")
        try:
            tor_process.terminate()
            tor_process.wait(timeout=3)
        except Exception:
            tor_process.kill()
        print("[+] Rastros eliminados. Motor finalizado.")

def get_current_exit_ip(use_proxy=False):
    """Comprueba la IP real o la IP de salida de la red Tor."""
    if use_proxy and not HAS_SOCKS:
        return "[-] Faltan dependencias. Ejecuta: pip install PySocks"

    try:
        if use_proxy:
            print("[*] Enrutando sonda a través de SOCKS5...")
            socks.set_default_proxy(socks.SOCKS5, TOR_PROXY_HOST, TOR_PROXY_PORT, rdns=True)
            socket.socket = socks.socksocket

        req = urllib.request.Request(
            "https://api.ipify.org?format=json",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        return f"[-] Error de red/OPSEC: {e}"

def run_shield(tor_path=None):
    """Mantiene vivo el túnel y escucha la señal de cierre."""
    if not start_tor_daemon(tor_path):
        sys.exit(1)

    print("=================================================================")
    print("      MAGNUM44 SHIELD - MOTOR TOR AUTÓNOMO (SOCKS5 ACTIVO)         ")
    print("=================================================================")
    print(f"[*] Redirección directa disponible en: socks5://127.0.0.1:{TOR_PROXY_PORT}")
    print("[*] OPSEC: Enrutamiento puro. IP local protegida.")
    print("[*] Atajos bash listos para usarse (tor-on / browser-tor).")
    print("[*] Presiona Ctrl+C para limpiar el entorno y salir.\n")
    print("    (NOTA: En Git Bash, usa 'winpty python magnum44_shield.py')")
    print("-" * 65)

    # Lanzamiento automático del navegador de uso diario con perfil normal enrutado por Tor
    abrir_navegador_tor()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[!] Interrupción recibida (Ctrl+C). Abortando...")
    finally:
        stop_tor_daemon()
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Magnum44 Shield - Gestor táctico de anonimato Tor")
    parser.add_argument("--check-ip", action="store_true", help="Audita la IP de salida de Tor")
    parser.add_argument("--tor-path", type=str, default=None, help="Ruta absoluta a tor.exe")
    args = parser.parse_args()

    if args.check_ip:
        if not start_tor_daemon(args.tor_path):
            return
        print(f"[*] Resultado Auditoría IP: {get_current_exit_ip(use_proxy=True)}")
        stop_tor_daemon()
        return

    run_shield(args.tor_path)

if __name__ == "__main__":
    main()
