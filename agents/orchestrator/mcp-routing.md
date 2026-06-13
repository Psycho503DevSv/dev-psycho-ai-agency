# MCP ROUTING: HERRAMIENTAS Y SEGURIDAD
## AI DevOS Orchestrator Module

### 1. GOBERNANZA DE HERRAMIENTAS
Ninguna herramienta MCP se invoca sin validación previa contra la `Capability-Matrix`.

### 2. ESPECIFICACIONES TÉCNICAS POR HERRAMIENTA

| Herramienta | Cuándo Usar | Cuándo NO Usar | Riesgo | Recuperación |
| :--- | :--- | :--- | :---: | :--- |
| **Filesystem** | Operaciones CRUD sobre código/docs. | Archivos de sistema operativo o .git/.env. | Bajo | Invertir cambios vía Git. |
| **Git** | Control de versiones, auditoría de cambios. | Commits sin descripción técnica o masivos. | Medio | `git reset --hard` (Solo con permiso). |
| **GitHub** | PRs, Issues, Auth, Remote Sync. | Credenciales de repo privado fuera de sesión. | Alto | Revocar tokens, cerrar sesión. |
| **Memory** | Persistencia de estados y lecciones. | Almacenamiento de código fuente masivo. | Bajo | Re-indexado semántico. |
| **Fetch** | Consultar documentación técnica externa. | IPs internas, descarga de binarios desconocidos. | Medio | Timeout, cache local. |
| **Docker** [STATUS: PLANNED] | Entornos de prueba, builds aislados. | Despliegue en producción sin review previo. | Alto | `docker kill`, limpiar contenedores. |
| **PostgreSQL** [STATUS: PLANNED] | Gestión de datos estructurados, schemas. | Drop/Truncate en Prod sin backup previo. | CRÍTICO | Restaurar desde `.sql` dump. |
| **Playwright** [STATUS: PLANNED] | Tests E2E, validación visual, crawling. | Sitios con `robots.txt` restrictivo o CAPTCHAs. | Medio | Captura de imagen (error log). |
| **Chrome DevTools** [STATUS: PLANNED] | Debugging de frontend, performance. | Inyección de scripts en sitios de terceros. | Medio | Reload de página. |
| **Figma** [STATUS: PLANNED] | Inspección de diseño, prototipado. | Edición de assets oficiales sin versionado. | Bajo | Historial de versiones Figma. |

### 3. COSTES Y PRIORIDADES
- **Prioridad 1 (Base):** Filesystem, Memory, Git. (Uso libre).
- **Prioridad 2 (Investigación):** Fetch, Playwright [STATUS: PLANNED], Chrome DevTools [STATUS: PLANNED]. (Uso moderado).
- **Prioridad 3 (Impacto):** Docker [STATUS: PLANNED], PostgreSQL [STATUS: PLANNED], GitHub. (Requiere autorización en Roadmap).

### 4. PROTOCOLO DE FALLBACK
Si una herramienta (ej. Playwright [STATUS: PLANNED]) falla continuamente por entorno:
1. Cambiar a herramienta de nivel inferior (ej. Fetch para HTML puro).
2. Si el fallo persiste, delegar al Usuario para intervención manual en terminal.

### 5. SEGURIDAD (SANITY CHECK)
- Todos los comandos enviados a `run_in_terminal` deben pasar por un Regex de sanitización para evitar `; rm -rf /`.
- Ningún path absoluto debe apuntar fuera de la carpeta del proyecto actual.
