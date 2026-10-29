🛡️ Magnum44 Shield v2.0

Magnum44 Shield es una herramienta de proxy de anonimato autónoma y portable orientada a operaciones de Red Team y pentesting (OPSEC). Establece túneles cifrados enrutando el tráfico local a través de la red Tor mediante un proxy SOCKS5 integrado, protegiendo la IP de origen, el NAT y el Gateway de tu máquina atacante o de auditoría.

Novedades en v2.0 (Plug & Play)

A diferencia de scripts tradicionales que dependen de servicios externos, Magnum44 Shield gestiona su propio motor de red:

Motor Tor Autónomo Integrado: No requiere instalar ni ejecutar el navegador Tor manualmente. El script localiza, inicializa y gestiona su propio proceso tor.exe (o tor en Linux) en segundo plano.

OPSEC First: Código 100% dinámico. No expone nombres de usuario, variables de entorno ni rutas estáticas de disco duro en el código fuente.

Limpieza Segura: Al interrumpir el proceso (Ctrl+C), el script mata limpiamente el demonio de Tor, sin dejar procesos huérfanos ni puertos abiertos consumiendo memoria.

Multiplataforma: Arquitectura unificada compatible nativamente con Linux, Git Bash y Windows PowerShell.

🛠️ Requisitos e Instalación

Solo necesitas Python 3, la librería de gestión de SOCKS y tener Tor instalado en el sistema (o colocar el binario dentro de la carpeta del proyecto para modo portable).

Clona el repositorio en tu entorno local:

git clone https://github.com/tolotelin99/magnum44-shield.git
cd magnum44-shield


Instala la dependencia de red requerida:

pip install PySocks


Uso de la Herramienta (Gestor Táctico)

⚠️ ATENCIÓN USUARIOS DE GIT BASH (WINDOWS):
Para que el script pueda cerrarse limpiamente con Ctrl+C sin dejar procesos fantasmas, debes anteponer el comando winpty (Ej: winpty python magnum44_shield.py). En Linux nativo o PowerShell, usa simplemente python.

1. Auditoría de OPSEC (Verificación de IP)

Inicia el motor de forma silenciosa, enruta una petición HTTPS para comprobar tu nueva IP de salida en la red Tor y destruye el circuito automáticamente:

python magnum44_shield.py --check-ip


2. Levantar el Escudo (Modo Motor Continuo)

Levanta el motor de red y expone el puerto local SOCKS5 (9050) para enrutar el tráfico de tu sistema. Se mantendrá activo hasta que lo interrumpas:

python magnum44_shield.py


3. Rutas de Motor Personalizadas (Modo Avanzado)

Si el script no detecta automáticamente tu instalación de Tor, puedes indicarle la ruta exacta del ejecutable:

python magnum44_shield.py --tor-path "/ruta/absoluta/a/tu/tor"


⚙️ Integración del Entorno (Terminal y Navegador)

Para maximizar el uso de Magnum44 Shield, configura estos atajos en tu terminal para enrutar herramientas (como curl, nmap) y navegadores de forma automática a través del túnel 9050.

Opción A: Entornos Linux y Git Bash

Añade las siguientes líneas al final de tu archivo ~/.bashrc o ~/.bash_profile:

# 1. Terminal Anónima (ON/OFF)
alias tor-on='export http_proxy="socks5h://127.0.0.1:9050" https_proxy="socks5h://127.0.0.1:9050" HTTP_PROXY="socks5h://127.0.0.1:9050" HTTPS_PROXY="socks5h://127.0.0.1:9050" ALL_PROXY="socks5h://127.0.0.1:9050"; echo "[+] Escudo activado a nivel sistema"'

alias tor-off='unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY; echo "[-] Escudo desactivado (IP Real)"'

# 2. Navegador Aislado (Chromium / Brave)
# ATENCIÓN OPSEC: Reemplaza las rutas genéricas por las ubicaciones reales en tu sistema.
alias browser-tor='"/RUTA/AL/NAVEGADOR/ejecutable" --proxy-server="socks5://127.0.0.1:9050" --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" --force-webrtc-ip-handling-policy=disable_non_proxied_udp --disable-background-networking --disable-sync --user-data-dir="/RUTA/AL/PROYECTO/perfil_tor_aislado" &'


Opción B: Entorno Windows PowerShell

En PowerShell, las variables de entorno se manejan de forma diferente. Puedes crear funciones en tu archivo $PROFILE o simplemente ejecutar estos comandos cuando necesites el escudo:

Activar el escudo (tor-on):

$env:http_proxy="socks5h://127.0.0.1:9050"; $env:https_proxy="socks5h://127.0.0.1:9050"; $env:ALL_PROXY="socks5h://127.0.0.1:9050"; Write-Host "[+] Escudo activado a nivel sistema" -ForegroundColor Green


Desactivar el escudo (tor-off):

Remove-Item Env:\http_proxy; Remove-Item Env:\https_proxy; Remove-Item Env:\ALL_PROXY; Write-Host "[-] Escudo desactivado (IP Real)" -ForegroundColor Red


Navegador Aislado:
(Ejecutar en una sola línea, asegurando cambiar las rutas)

Start-Process -FilePath "C:\RUTA\AL\NAVEGADOR\ejecutable.exe" -ArgumentList '--proxy-server="socks5://127.0.0.1:9050" --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" --force-webrtc-ip-handling-policy=disable_non_proxied_udp --disable-background-networking --disable-sync --user-data-dir="C:\RUTA\AL\PROYECTO\perfil_tor_aislado"'
