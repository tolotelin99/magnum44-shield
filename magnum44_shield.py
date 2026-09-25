import argparse
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import socks  # Requiere: pip install PySocks

# Configuración del proxy SOCKS5 interno
TOR_PROXY_HOST = "127.0.0.1"
TOR_PROXY_PORT = 9050  # Puerto estándar del demonio de Tor autónomo
tor_process = None


def is_port_in_use(port):
  """Verifica si un puerto local ya está ocupado."""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    return s.connect_ex((TOR_PROXY_HOST, port)) == 0


def start_tor_daemon(custom_tor_path=None):
  """Intenta iniciar el motor de Tor automáticamente buscando en el sistema o ruta personalizada."""
  global tor_process, TOR_PROXY_PORT
  ports_to_check = [9050, 9150]

  # 1. Verificar si ya hay algún Tor corriendo en los puertos comunes
  for port in ports_to_check:
    if is_port_in_use(port):
      print(f"[*] Se detectó un motor de Tor activo en el puerto {port}.")
      TOR_PROXY_PORT = port
      return True

  print(
      "[*] No se detectó Tor activo. Buscando el ejecutable en el sistema..."
  )

  tor_executable = None

  # Si el usuario pasó una ruta personalizada por parámetro, la priorizamos
  if custom_tor_path and os.path.exists(custom_tor_path):
    tor_executable = custom_tor_path
  else:
    # OPSEC: Rutas dinámicas y relativas (no revela nombres de usuario en el código)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_home = os.path.expanduser("~")
    
    common_tor_paths = [
        # 1. Versión portable: Busca en la misma carpeta del script (Máxima prioridad)
        os.path.join(base_dir, "Tor", "tor.exe"),
        
        # 2. Rutas dinámicas del sistema
        os.path.join(user_home, "OneDrive", "Escritorio", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
        os.path.join(user_home, "Desktop", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
        os.path.join(user_home, "Downloads", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
        os.path.join(user_home, "AppData", "Local", "Tor Browser", "Browser", "TorBrowser", "Tor", "tor.exe"),
        "C:\\Program Files\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
        "C:\\Program Files (x86)\\Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe",
    ]

    if shutil.which("tor"):
      tor_executable = "tor"
    else:
      for path in common_tor_paths:
        if os.path.exists(path):
          tor_executable = path
          break

  if not tor_executable:
    print(
        "[-] Error crítico: No se encontró 'tor.exe' automáticamente en tu equipo."
    )
    print(
        "    Sugerencia: Usa el parámetro --tor-path para indicarle dónde está"
    )
    return False

  try:
    print(f"[*] Iniciando motor de Tor desde: {tor_executable}")
    tor_process = subprocess.Popen(
        [tor_executable, "--SocksPort", str(TOR_PROXY_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("[*] Esperando a que el circuito de Tor se estabilice...")

    for _ in range(15):
      if is_port_in_use(TOR_PROXY_PORT):
        print(f"[+] ¡Motor Tor autónomo activo en el puerto {TOR_PROXY_PORT}!")
        return True
      time.sleep(1)

    print("[-] El motor de Tor tardó demasiado en responder.")
    return False

  except Exception as e:
    print(f"[-] Error al intentar lanzar el motor de Tor: {e}")
    return False


def stop_tor_daemon():
  """Detiene el proceso de Tor si fue iniciado por el script."""
  global tor_process
  if tor_process:
    print("[*] Deteniendo el motor de Tor autónomo...")
    try:
      tor_process.terminate()
      tor_process.wait(timeout=3)
    except Exception:
      tor_process.kill()
    print("[+] Motor de Tor finalizado correctamente.")


def get_current_exit_ip(use_proxy=False):
  """Consulta la IP pública actual a través de la red Tor (SOCKS5)."""
  try:
    if use_proxy:
      print("[*] Enrutando consulta a través del circuito de Tor...")
      socks.set_default_proxy(
          socks.SOCKS5, TOR_PROXY_HOST, TOR_PROXY_PORT, rdns=True
      )
      socket.socket = socks.socksocket
    else:
      socket.socket = socket.socket

    req = urllib.request.Request(
        "https://api.ipify.org?format=json",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
      return response.read().decode("utf-8")
  except Exception as e:
    return f"[-] Error de conexión con Tor: {e}"


def handle_client_connection(client_socket):
  """Maneja el túnel CONNECT de forma asíncrona sin bloquear la terminal."""
  target_socket = None
  try:
    request_data = client_socket.recv(4096)
    if not request_data:
      return

    first_line = request_data.decode("utf-8", errors="ignore").split("\n")[0]

    if "CONNECT" in first_line:
      parts = first_line.split(" ")
      if len(parts) >= 2:
        target_host_port = parts[1].split(":")
        target_host = target_host_port[0]
        target_port = int(target_host_port[1]) if len(target_host_port) > 1 else 443

        target_socket = socks.socksocket()
        target_socket.set_proxy(socks.SOCKS5, TOR_PROXY_HOST, TOR_PROXY_PORT)
        target_socket.connect((target_host, target_port))

        client_socket.sendall(
            b"HTTP/1.1 200 Connection Established\r\nProxy-Agent:"
            b" Magnum44-Shield/Autonomous\r\n\r\n"
        )

        def forward(src, dst):
          try:
            while True:
              data = src.recv(8192)
              if not data:
                break
              dst.sendall(data)
          except Exception:
            pass
          finally:
            try:
              src.close()
            except Exception:
              pass
            try:
              dst.close()
            except Exception:
              pass

        t1 = threading.Thread(target=forward, args=(client_socket, target_socket))
        t2 = threading.Thread(target=forward, args=(target_socket, client_socket))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        return

    client_socket.sendall(
        b"HTTP/1.1 500 Internal Server Error\r\n\r\nSolo se soportan tuneles"
        b" HTTPS CONNECT."
    )
  except Exception:
    pass


def start_shield_server(local_port, tor_path=None):
  if not start_tor_daemon(tor_path):
    sys.exit(1)

  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  try:
    server.bind(("127.0.0.1", local_port))
    server.listen(100)
    server.settimeout(1.0)

    print("=================================================================")
    print("      MAGNUM44 SHIELD - ESCUDO AUTÓNOMO & MOTOR TOR (SOCKS5)     ")
    print("=================================================================")
    print(f"[*] Escudo activo en local: http://127.0.0.1:{local_port}")
    print(
        f"[*] Redirección forzada al circuito autónomo de Tor (127.0.0.1:{TOR_PROXY_PORT})."
    )
    print("[*] Tu IP real, NAT y Gateway están protegidos bajo anonimato.")
    print("[*] Presiona Ctrl+C para desactivar el escudo.\n")
    print("-" * 65)

    while True:
      try:
        client_sock, address = server.accept()
        client_handler = threading.Thread(
            target=handle_client_connection, args=(client_sock,)
        )
        client_handler.daemon = True
        client_handler.start()
      except socket.timeout:
        continue

  except KeyboardInterrupt:
    print("\n[!] Desactivando Magnum44 Shield de forma segura...")
  finally:
    stop_tor_daemon()
    sys.exit(0)


def main():
  parser = argparse.ArgumentParser(
      description=(
          "Magnum44 Shield - Escudo de anonimización autónomo basado en Tor"
      )
  )
  parser.add_argument(
      "-p",
      "--port",
      type=int,
      default=8888,
      help="Puerto local del escudo (Por defecto: 8888)",
  )
  parser.add_argument(
      "--check-ip",
      action="store_true",
      help=(
          "Consulta la IP de salida actual a través del circuito Tor autónomo"
      ),
  )
  parser.add_argument(
      "--tor-path",
      type=str,
      default=None,
      help="Ruta absoluta al ejecutable tor.exe de Tor Browser",
  )

  args = parser.parse_args()

  if args.check_ip:
    if not start_tor_daemon(args.tor_path):
      return
    print(f"[*] Resultado: {get_current_exit_ip(use_proxy=True)}")
    stop_tor_daemon()
    return

  start_shield_server(args.port, args.tor_path)


if __name__ == "__main__":
  main()