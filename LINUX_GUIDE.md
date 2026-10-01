```markdown
# 🐧 Guía de Instalación y Uso en Linux

Aunque Magnum44 Shield incluye un motor portable `.exe` para entornos Windows (Plug & Play), el script está diseñado para ser totalmente compatible con distribuciones Linux (Kali Linux, Parrot OS, Debian, Ubuntu, etc.) detectando e integrándose con el servicio nativo de Tor.

## 1. Preparación del Sistema

Instala el motor oficial de Tor y el gestor de paquetes de Python (`pip`):

```bash
sudo apt update
sudo apt install tor python3-pip -y

```

## 2. Instalación

Clona el repositorio e instala las dependencias mediante el archivo `requirements.txt`:

```bash
git clone [https://github.com/tolotelin99/magnum44-shield.git](https://github.com/tolotelin99/magnum44-shield.git)
cd magnum44-shield
pip3 install -r requirements.txt

```

## 3. Ejecución del Escudo

El script detectará automáticamente el servicio Tor de tu sistema operativo. Asegúrate de ejecutarlo usando `python3`:

**Prueba rápida de IP (Comprobación de circuito):**

```bash
python3 magnum44_shield.py --check-ip

```

**Iniciar el servidor proxy de forma continua:**

```bash
python3 magnum44_shield.py

```

---

## 4. Atajos de Entorno (Opcional)

Para facilitar el enrutamiento automático de herramientas (`curl`, `nmap`, etc.) y navegadores por el túnel `9050`, puedes agregar estos alias a tu archivo `~/.bashrc` o `~/.zshrc`:

```bash
# 1. Terminal Anónima (ON/OFF)
alias tor-on='export http_proxy="socks5h://127.0.0.1:9050" https_proxy="socks5h://127.0.0.1:9050" HTTP_PROXY="socks5h://127.0.0.1:9050" HTTPS_PROXY="socks5h://127.0.0.1:9050" ALL_PROXY="socks5h://127.0.0.1:9050"; echo "[+] Escudo activado a nivel sistema"'
alias tor-off='unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY; echo "[-] Escudo desactivado (IP Real)"'

# 2. Navegador Aislado (Ejemplo con Brave Browser)
alias brave-tor='brave-browser --proxy-server="socks5://127.0.0.1:9050" --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" --user-data-dir="./perfil_tor_aislado" &'

```

```

### 2. Súbelo desde tu terminal Git Bash
Una vez guardado el archivo, ve a tu terminal y ejecuta estos comandos uno por uno para subir la nueva guía a GitHub:

```bash
git add LINUX_GUIDE.md

```

```bash
git commit -m "Añadida guía oficial de instalación y despliegue para Linux"

```

```bash
git push origin main

```
