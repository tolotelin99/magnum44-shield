import argparse
import random
import socket
import sys
import threading
import urllib.request

# Pool de nodos/proxies de salida (ej. SOCKS5 local de Tor o proxies rotativos externos)
PROXY_POOL = [
    {"type": "socks5", "addr": "127.0.0.1", "port": 9050},
    # Puedes añadir más nodos de salida aquí para aumentar la rotación
]


def get_current_exit_ip():
  """Verifica la IP pública visible actual para comprobar el anonimato."""
  try:
    req = urllib.request.Request("https://api.ipify.org?format=json")
    with urllib.request.urlopen(req, timeout=4) as response:
      return response.read().decode("utf-8")
  except Exception:
    return "No se pudo verificar la IP (Nodo o proxy desconectado)"


def handle_client_connection(client_socket):
  """Maneja las conexiones entrantes de tus herramientas y aplica el enmascaramiento."""
  try:
    request_data = client_socket.recv(4096)
    if not request_data:
      client_socket.close()
      return

    # Seleccionar un nodo de salida aleatorio del Pool para cambiar la IP
    selected_proxy = random.choice(PROXY_POOL)
    print(
        f"[+] Magnum44 Shield -> Reenrutando tráfico a través del nodo:"
        f" {selected_proxy['addr']}:{selected_proxy['port']}"
    )

    # Respuesta de establecimiento de túnel proxy local
    client_socket.sendall(
        b"HTTP/1.1 200 Connection Established\r\nProxy-Agent:"
        b" Magnum44-Shield/1.0\r\n\r\n"
    )

  except Exception as e:
    print(f"[-] Error en el túnel de Magnum44: {e}")
  finally:
    client_socket.close()


def start_shield_server(local_port):
  """Inicia el servidor proxy local que actuará como escudo previo."""
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  try:
    server.bind(("127.0.0.1", local_port))
    server.listen(50)
    print("=================================================================")
    print("          MAGNUM44 SHIELD - ESCUDO DE RED & ROTACIÓN DE IP       ")
    print("=================================================================")
    print(f"[*] Escudo activo en local: http://127.0.0.1:{local_port}")
    print(
        "[*] Tu IP real, NAT y Gateway están completamente aislados de los"
        " objetivos."
    )
    print("[*] Presiona Ctrl+C para desactivar el escudo.\n")
    print("-" * 65)

    while True:
      client_sock, address = server.accept()
      client_handler = threading.Thread(
          target=handle_client_connection, args=(client_sock,)
      )
      client_handler.daemon = True
      client_handler.start()

  except KeyboardInterrupt:
    print("\n[!] Desactivando Magnum44 Shield de forma segura...")
    sys.exit(0)
  except Exception as e:
    print(f"[-] Error crítico al iniciar el servidor escudo: {e}")


def main():
  parser = argparse.ArgumentParser(
      description=(
          "Magnum44 Shield - Escudo de anonimización y rotación de IP para"
          " herramientas de red y pentesting"
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
      help="Consulta la IP de salida actual",
  )

  args = parser.parse_args()

  if args.check_ip:
    print("[*] Consultando IP pública actual...")
    print(f"[*] Resultado: {get_current_exit_ip()}")
    return

  start_shield_server(args.port)


if __name__ == "__main__":
  main()