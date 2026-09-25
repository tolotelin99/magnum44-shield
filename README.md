# Magnum44 Shield v1.0

**Magnum44 Shield** es una herramienta de privacidad y anonimización de red desarrollada en Python bajo la filosofía Unix. Actúa como un proxy local intermedio (wrapper de red) para enmascarar tu IP real, aislar tu NAT y ocultar tu Gateway antes de ejecutar tareas de escaneo, reconocimiento o *fuzzing*.

---

##  Características Principales

- **Escudo Local Invisible**: Levanta un servidor proxy local (`127.0.0.1`) que intercepta el tráfico de tus herramientas de seguridad.
- **Aislamiento de Red**: Previene que tu IP real y los identificadores de tu red local se expongan a los servidores de destino.
- **Verificación de Anonimato**: Funciones integradas para consultar la IP de salida actual antes de iniciar operaciones.
- **Modularidad**: Diseñado para operar independientemente y combinarse con proxies de salida o redes anónimas.

---

##  Instalación

Clona el repositorio en tu sistema local:

```bash
git clone [https://github.com/tolotelin99/magnum44-shield.git](https://github.com/tolotelin99/magnum44-shield.git)
cd magnum44-shield
