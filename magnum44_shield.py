import argparse
import socket
import sys
import threading
import urllib.request
import socks  # Requiere: pip install PySocks

# Configuración del nodo local de Tor (SOCKS5)
TOR_PROXY_HOST = "127.0.0.1"
TOR_PROXY_PORT = 9150


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
      # Restablecer socket normal si no se usa proxy
      socket.socket = socket._socketobject if hasattr(socket, '_socketobject') else socket.socket

    # Usamos HTTPS ya que Tor cifra el tráfico de extremo a extremo de forma segura
    req = urllib.request.Request(
        "https://api.ipify.org?format=json",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as response:
      return response.read().decode("utf-8")
  except Exception as e:
    return (
        f"[-] Error de conexión con Tor (¿Está Tor o Tor Browser abierto en el"
        f" puerto {TOR_PROXY_PORT}?): {e}"
    )


def handle_client_connection(client_socket):
  """Intercepta el tráfico local, establece el túnel SOCKS5 con Tor y reenvía los datos de forma bidireccional."""
  target_socket = None
  try:
    # Crear socket SOCKS5 conectado a Tor
    target_socket = socks.socksocket()
    target_socket.set_proxy(socks.SOCKS5, TOR_PROXY_HOST, TOR_PROXY_PORT)
    
    # Recibir la petición inicial del cliente
    request_data = client_socket.recv(4096)
    if not request_data:
      return

    # Extraer el host y puerto de destino si es una petición CONNECT (HTTPS)
    first_line = request_data.decode("utf-8", errors="ignore").split("\n")[0]
    
    if "CONNECT" in first_line:
      # Ejemplo: CONNECT api.ipify.org:443 HTTP/1.1
      parts = first_line.split(" ")
      if len(parts) >= 2:
        target_host_port = parts[1].split(":")
        target_host = target_host_port[0]
        target_port = int(target_host_port[1]) if len(target_host_port) > 1 else 443

        # Conectamos a través del proxy SOCKS5 de Tor
        target_socket.connect((target_host, target_port))
        
        # Respondemos al cliente local que el túnel está establecido
        client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        # Función para retransmitir datos en un hilo
        def forward(source, destination):
          try:
            while True:
              data = source.recv(8192)
              if not data:
                break
              destination.sendall(data)
          except Exception:
            pass
          finally:
            try:
              source.shutdown(socket.SHUT_RD)
            except Exception:
              pass
            try:
              destination.shutdown(socket.SHUT_WR)
            except Exception:
              pass

        # Lanzar hilos bidireccionales
        t1 = threading.Thread(target=forward, args=(client_socket, target_socket))
        t2 = threading.Thread(target=forward, args=(target_socket, client_socket))
        t1.daemon = True
        t2.daemon = True
        t1.start()
        t2.start()
        
        # Esperar a que terminen
        t1.join()
        t2.join()
        return

    # Si es una petición HTTP plana ordinaria (no CONNECT)
    client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\nSolo se soportan tuneles HTTPS CONNECT por ahora.")
    
  except Exception as e:
    print(f"[-] Error en el reenvío del túnel: {e}")
  finally:
    client_socket.close()
    if target_socket:
      target_socket.close()


def start_shield_server(local_port):
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  try:
    server.bind(("127.0.0.1", local_port))
    server.listen(100)
    server.settimeout(
        1.0
    )  # <-- Esto permite que Ctrl+C responda rápido en Windows
    print("=================================================================")
    print("       MAGNUM44 SHIELD - ESCUDO DE RED & MOTOR TOR (SOCKS5)      ")
    print("=================================================================")
    print(f"[*] Escudo activo en local: http://127.0.0.1:{local_port}")
    print(
        f"[*] Redirección forzada al circuito de Tor (127.0.0.1:{TOR_PROXY_PORT})."
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
        continue  # Permite que el bucle verifique KeyboardInterrupt cada segundo

  except KeyboardInterrupt:
    print("\n[!] Desactivando Magnum44 Shield de forma segura...")
    sys.exit(0)
  except Exception as e:
    print(f"[-] Error en el servidor del escudo: {e}")


def main():
  parser = argparse.ArgumentParser(
      description=(
          "Magnum44 Shield - Escudo de anonimización basado en Tor SOCKS5"
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
          "Consulta la IP de salida actual saliendo a través del circuito Tor"
      ),
  )

  args = parser.parse_args()

  if args.check_ip:
    print("[*] Consultando IP de salida a través del circuito Tor...")
    print(f"[*] Resultado: {get_current_exit_ip(use_proxy=True)}")
    return

  start_shield_server(args.port)


if __name__ == "__main__":
  main()