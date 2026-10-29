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

# Configuración del proxy SOCKS5 interno
TOR_PROXY_HOST = "127.0.0.1"
TOR_PROXY_PORT = 9050  # Puerto estándar del demonio de Tor autónomo
tor_process = None


def is_port_in_use(port):
    """Verifica si un puerto local ya está ocupado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((TOR_PROXY_HOST, port)) == 0


def start_tor_daemon(custom_tor_path=None):
    """Inicia el motor de Tor localizando el ejecutable de forma dinámica y sigilosa."""
    global tor_process, TOR_PROXY_PORT
    ports_to_check = [9050, 9150]

    # 1. Verificar si ya hay un circuito activo
    for port in ports_to_check:
        if is_port_in_use(port):
            print(f"[*] Circuito Tor ya detectado y activo en el puerto {port}.")
            TOR_PROXY_PORT = port
            return True

    print("[*] No se detectó Tor activo. Buscando motor de red...")
    tor_executable = None

    if custom_tor_path and os.path.exists(custom_tor_path):
        tor_executable = custom_tor_path
    else:
        # OPSEC: Cálculo dinámico de rutas. Sin strings quemados de usuarios o SO.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        user_home = os.path.expanduser("~")
        sys_drive = os.environ.get("SystemDrive", "C:")
        
        common_tor_paths = [
            os.path.join(base_dir, "Tor", "tor.exe"),  # 1. Portable local
            os.path.join(user_home, "Desktop", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
            os.path.join(user_home, "Downloads", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
            os.path.join(sys_drive + "\\", "Program Files", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
            os.path.join(sys_drive + "\\", "Program Files (x86)", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
        ]

        if shutil.which("tor"):
            tor_executable = "tor"
        else:
            for path in common_tor_paths:
                if os.path.exists(path):
                    tor_executable = path
                    break

    if not tor_executable:
        print("[-] Error OPSEC: No se encontró 'tor.exe' en rutas estándar.")
        print("    Uso: python magnum44_shield.py --tor-path <ruta_al_ejecutable>")
        return False

    try:
        print(f"[*] Levantando motor desde: {tor_executable}")
        # Se lanza sin abrir ventanas (DEVNULL) para mantener el sigilo
        tor_process = subprocess.Popen(
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
        else:
            socket.socket = socket.socket

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
    print("      MAGNUM44 SHIELD - MOTOR TOR AUTÓNOMO (SOCKS5 ACTIVO)       ")
    print("=================================================================")
    print(f"[*] Redirección directa disponible en: socks5://127.0.0.1:{TOR_PROXY_PORT}")
    print("[*] OPSEC: Enrutamiento puro. IP local protegida.")
    print("[*] Atajos bash listos para usarse (tor-on / browser-tor).")
    print("[*] Presiona Ctrl+C para limpiar el entorno y salir.\n")
    print("    (NOTA: En Git Bash, usa 'winpty python magnum44_shield.py')")
    print("-" * 65)

    try:
        # Bucle de bajo consumo de CPU esperando interrupción
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