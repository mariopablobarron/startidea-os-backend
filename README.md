# Startidea OS

Base de proyecto lista para despliegue en Coolify sobre VPS.

## Estructura

- app/: frontend estatico inicial
- Dockerfile: imagen lista para Coolify
- nginx.conf: configuracion de servidor web
- docker-compose.yml: ejecucion local rapida

## Ejecutar local

1. Construir y levantar:

   docker compose up --build

2. Abrir en navegador:

   http://localhost:8080

## Despliegue en Coolify (VPS)

1. Sube este repositorio a GitHub/GitLab.
2. En Coolify, crea un nuevo Resource desde Git.
3. Selecciona este repo y rama principal.
4. Build Pack: Dockerfile.
5. Puerto interno: 80.
6. Configura dominio y SSL (Lets Encrypt) desde Coolify.
7. Pulsa Deploy.

## Flujo de trabajo recomendado

1. Desarrolla cambios en una rama.
2. Haz push al repo remoto.
3. En Coolify activa Auto Deploy por push, o despliega manualmente.
4. Valida logs y healthcheck desde el panel.

## Siguientes pasos sugeridos

- Sustituir app/ por tu aplicacion real (frontend, API o full stack).
- Agregar variables de entorno y secretos desde Coolify.
- Configurar staging y produccion con ramas separadas.
