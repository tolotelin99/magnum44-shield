```markdown
# ️ Magnum44 Shield v2.0

**Magnum44 Shield** es una herramienta de proxy de anonimato autónoma y portable orientada a operaciones de Red Team y pentesting (OPSEC). Establece túneles cifrados enrutando el tráfico local a través de la red Tor mediante un proxy SOCKS5 integrado, protegiendo la IP de origen, el NAT y el Gateway de tu máquina atacante o de auditoría.

---

##  Novedades en v2.0 (Plug & Play)

A diferencia de scripts tradicionales que dependen de servicios externos, **Magnum44 Shield gestiona su propio motor de red**:
* **Motor Tor Autónomo Integrado:** No requiere instalar ni ejecutar "Tor Browser". El script localiza, inicializa y gestiona su propio proceso `tor.exe` en segundo plano.
* **OPSEC First:** Código 100% dinámico. No expone nombres de usuario, variables de entorno ni rutas de disco duro en el código fuente.
* **Limpieza Segura:** Al interrumpir el proceso (`Ctrl+C`), el script mata limpiamente el demonio de Tor, sin dejar procesos huérfanos ni puertos abiertos.
* **Portabilidad Total:** Clona el repositorio, instálalo en un USB o ejecútalo en cualquier máquina Windows al instante mediante rutas relativas.

---

##  Requisitos e Instalación

Solo necesitas Python 3 y la librería de gestión de SOCKS.

1. Clona el repositorio en tu sistema local:
```bash
git clone [https://github.com/tolotelin99/magnum44-shield.git](https://github.com/tolotelin99/magnum44-shield.git)
cd magnum44-shield

```

2. Instala las dependencias:

```bash
pip install PySocks

```

---

##  Uso de la Herramienta (Motor Tor)

### 1. Verificación rápida de Anonimato (Prueba de IP)

Inicia el motor de forma silenciosa, enruta una petición HTTPS para comprobar tu nueva IP de salida en la red Tor y apaga el motor:

```bash
python magnum44_shield.py --check-ip

```

### 2. Iniciar el Escudo (Modo Motor Continuo)

Levanta el motor de red y expone el puerto local SOCKS5 (`9050`) para enrutar tráfico de otras herramientas, manteniéndolo activo:

```bash
python magnum44_shield.py

```

### 3. Rutas de Motor Personalizadas (Avanzado)

Si deseas utilizar una instalación específica del motor Tor en tu sistema en lugar del motor integrado portable:

```bash
python magnum44_shield.py --check-ip --tor-path "C:\Ruta\a\tu\tor.exe"

```

---

##  Integración del Entorno (Terminal y Navegador)

Para maximizar el uso de **Magnum44 Shield**, se recomienda configurar atajos (alias) en tu terminal (Ej: Git Bash / `.bashrc` en Linux) para enrutar herramientas (como `curl`, `nmap`, `wget`) y navegadores de forma automática a través del túnel `9050`.

Añade las siguientes líneas a tu archivo `~/.bashrc`:

```bash
# ==========================================
# MAGNUM44 SHIELD - ALIAS DE ENTORNO
# ==========================================

# 1. Terminal Anónima (ON/OFF)
# Enruta todo el tráfico de la consola (HTTP/HTTPS) por Tor SOCKS5, forzando DNS remoto (socks5h).
alias tor-on='export http_proxy="socks5h://127.0.0.1:9050" https_proxy="socks5h://127.0.0.1:9050" HTTP_PROXY="socks5h://127.0.0.1:9050" HTTPS_PROXY="socks5h://127.0.0.1:9050" ALL_PROXY="socks5h://127.0.0.1:9050"; echo "[+] Escudo activado a nivel sistema"'
alias tor-off='unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY; echo "[-] Escudo desactivado (IP Real)"'

# 2. Navegador Aislado (Brave / Chromium)
# Abre una sesión limpia, sin historial ni cookies, forzando el proxy y resolución DNS remota.
# Nota: Ajusta la ruta a tu ejecutable de Brave según tu sistema.
alias brave-tor='"C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe" --proxy-server="socks5://127.0.0.1:9050" --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" --user-data-dir="./perfil_tor_aislado" &'

```

### ¿Cómo usar los atajos?

* Asegúrate de que `magnum44_shield.py` esté en ejecución.
* Escribe `tor-on` en tu terminal para que comandos como `curl https://api.ipify.org` salgan con IP anónima.
* Escribe `brave-tor` para lanzar un navegador desechable, seguro e invisible.

---

## ⚠️ Aviso Legal

*Magnum44 Shield fue desarrollado exclusivamente con fines educativos y para su uso en auditorías de ciberseguridad autorizadas (Red Teaming / Pentesting). El creador no se hace responsable del mal uso de esta herramienta ni del tráfico enrutado a través de ella.*

```

```