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

## Despliegue administrativo de workflows n8n

`deploy_n8n.py` realiza escrituras administrativas. Antes de ejecutarlo:

1. Crea una clave nueva en la instancia autorizada. No reutilices ninguna clave
   que haya aparecido en Git o en un chat.
2. Expón de forma temporal `N8N_API_URL` con una URL `https://` terminada en
   `/api/v1`, `N8N_API_KEY` y `N8N_TELEGRAM_CREDENTIAL_ID` desde tu gestor de
   secretos. El script falla si falta alguna o si la URL usa HTTP.
3. Opcionalmente configura `N8N_WORKFLOW_DIR`; por defecto se usa la raíz del
   repositorio.
4. Ejecuta `python3 deploy_n8n.py` sólo tras revisar la instancia y el alcance
   de la operación. Después elimina las variables temporales del proceso.

Nunca guardes la clave real en `.env.example`, en el repositorio ni en la línea
de comandos. La clave que estuvo versionada históricamente debe considerarse
comprometida y no debe volver a habilitarse.

## Siguientes pasos sugeridos

- Sustituir app/ por tu aplicacion real (frontend, API o full stack).
- Agregar variables de entorno y secretos desde Coolify.
- Configurar staging y produccion con ramas separadas.
