#  Magnum44 Shield v2.0

**Magnum44 Shield** es una herramienta de proxy de anonimato autónoma y portable orientada a operaciones de Red Team y pentesting (OPSEC). Establece túneles cifrados enrutando el tráfico local a través de la red Tor mediante un proxy SOCKS5 integrado, protegiendo la IP de origen, el NAT y el Gateway.

---

##  Novedades en v2.0 (Plug & Play)

A diferencia de scripts tradicionales que dependen de servicios externos, **Magnum44 Shield gestiona su propio motor de red**.
* **Motor Tor Autónomo Integrado:** No requiere instalar ni ejecutar "Tor Browser". El script localiza, inicializa y gestiona su propio proceso `tor.exe` en segundo plano.
* **OPSEC First:** Código 100% dinámico. No expone nombres de usuario, variables de entorno ni rutas de disco duro en el código fuente.
* **Limpieza Segura:** Al interrumpir el proceso (`Ctrl+C`), el script mata limpiamente el demonio de Tor, sin dejar procesos huérfanos ni puertos abiertos.
* **Portabilidad Total:** Clona el repositorio, instálalo en un USB o ejecútalo en cualquier máquina Windows al instante.

---

##  Requisitos

Solo necesitas Python 3 y la librería de gestión de SOCKS:

`pip install PySocks`

---

##  Uso de la Herramienta

### 1. Verificación rápida de Anonimato (Prueba de IP)
Inicia el motor de forma silenciosa, enruta una petición HTTPs para comprobar tu nueva IP de salida en la red Tor y apaga el motor:

`python magnum44_shield.py --check-ip`

### 2. Iniciar el Escudo (Modo Proxy Servidor)
Levanta el motor de red y expone un puerto local (por defecto `8888`) para enrutar tráfico de otras herramientas a través de la red Tor:

`python magnum44_shield.py -p 8888`

### 3. Rutas de Motor Personalizadas (Avanzado)
Si deseas utilizar una instalación específica del motor Tor en tu sistema en lugar del motor integrado portable:

`python magnum44_shield.py --check-ip --tor-path "C:\Ruta\a\tu\tor.exe"`

---

## ⚠️ Aviso Legal
*Magnum44 Shield fue desarrollado con fines educativos y para su uso en auditorías de ciberseguridad autorizadas. El creador no se hace responsable del mal uso de esta herramienta ni del tráfico enrutado a través de ella.*
