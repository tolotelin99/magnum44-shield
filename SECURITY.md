# 🛡️ Política de Seguridad (Magnum44 Shield)

La seguridad y la integridad operacional (OPSEC) son las principales prioridades de este proyecto. Este documento describe nuestro modelo de amenazas, las políticas de soporte y cómo reportar vulnerabilidades de manera responsable.

## 📌 Versiones Soportadas

Actualmente, solo la última versión del script recibe actualizaciones de seguridad.

| Versión | Soporte de Seguridad | Notas |
| :--- | :--- | :--- |
| **v2.0.x** | ✅ Soportada | Arquitectura SOCKS5 directa, sin puente HTTP. |
| < v2.0 | ❌ Descontinuada | Vulnerable a fugas de WebRTC e Information Disclosure. Se recomienda actualizar inmediatamente. |

---

## 🎯 Modelo de Amenazas (Threat Model)

Magnum44 Shield está diseñado específicamente para **Operaciones de Red Team, CTFs y Pentesting**. 

**✅ Lo que Magnum44 Shield PROTEGE:**
* **Ocultamiento de IP de Origen:** Enruta el tráfico TCP de tu terminal a través de la red Tor.
* **Resolución DNS Segura:** Si se utilizan los alias correctos (`socks5h://`), previene fugas locales de DNS.
* **Aislamiento de Entorno:** Permite lanzar navegadores sin estado (sin cookies ni historial previo) para auditorías limpias.

**❌ Lo que Magnum44 Shield NO PROTEGE (Fuera del alcance):**
* **Tráfico No Cifrado (HTTP):** Los nodos de salida de Tor pueden interceptar tráfico. Siempre utiliza protocolos seguros (HTTPS, SSH).
* **Fugas por Capa de Aplicación:** Si utilizas el proxy en un navegador normal sin las *flags* anti-WebRTC documentadas en el README, tu IP real se filtrará mediante tráfico UDP.
* **Ataques de día cero (0-days):** El script no protege contra exploits dirigidos al motor del navegador o binarios maliciosos descargados.

---

## 🚨 Avisos de Seguridad Críticos (Security Advisories)

### [Resuelto en v2.0] Riesgo de Fuga por WebRTC y Browser Fingerprinting
Se detectó que el uso de navegadores basados en Chromium a través de proxys estándar SOCKS5 permite fugas de la IP real mediante el protocolo UDP de WebRTC. 
* **Solución mitigada:** A partir de la versión 2.0, la documentación oficial exige el uso del parámetro `--force-webrtc-ip-handling-policy=disable_non_proxied_udp` en los alias del navegador para cortar el tráfico UDP local.

### [Resuelto en v2.0] Information Disclosure en Rutas
Las versiones anteriores quemaban rutas estáticas en el código fuente, revelando información del sistema base del atacante.
* **Solución mitigada:** La v2.0 implementa búsqueda dinámica de binarios usando variables de entorno y `shutil.which`.

---

## 📬 Cómo reportar una vulnerabilidad

Si descubres un problema que afecte la Seguridad Operacional (OPSEC), permita la filtración de direcciones IP, DNS, o exponga el sistema host, **por favor no abras un "Issue" público**.
comentanos y lo resolveremos inmediatamente.

**Incluye en tu reporte:**
1. Descripción detallada de la vulnerabilidad (Ej: Fuga de DNS en Windows 11).
2. Pasos para reproducir el problema.
3. Evidencia (Capturas de Wireshark, logs de red, o reportes de browserleaks.com).

Recibirás una respuesta confirmando la recepción del reporte en un plazo máximo de 48 horas.