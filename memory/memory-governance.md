# GOBERNANZA DE LA CAPA DE MEMORIA (MEMORY LAYER)

## 1. ESTRUCTURA DE ALMACENAMIENTO
- `/memory/projects/`: Una carpeta por proyecto (`[id]-[nombre]`).
- `/memory/decisions/`: Log cronológico de decisiones arquitectónicas (`YYYY-MM-DD-decision.md`).
- `/memory/lessons-learned/`: Base de datos de errores y soluciones.
- `/memory/sessions/`: Contexto persistente de sesiones de chat (`YYYY-MM-DD-session-id.json`).
- `/memory/patterns/`: Snippets y flujos reutilizables.

## 2. CONVENCIÓN DE NOMBRADO
- **Archivos:** `kebab-case`.
- **Prefijos:** Usar fechas ISO `YYYY-MM-DD-` para logs y sesiones.
- **Idioma:** Contenido íntegramente en español.

## 3. POLÍTICA DE RETENCIÓN Y RECUPERACIÓN (RETRIEVAL)
1. **Memoria de Trabajo:** (Sesión actual) Alta prioridad.
2. **Memoria de Proyecto:** (Carpeta /projects) Consultada por agentes especialistas.
3. **Memoria Histórica:** (Decisiones/Lecciones) Consultada por Orchestrator y Knowledge Manager para evitar repetir errores.

## 4. ESTRATEGIA DE BÚSQUEDA
- Los agentes deben usar `grep_search` o herramientas de búsqueda MCP sobre `/memory` antes de proponer soluciones nuevas.
- El Knowledge Manager consolidará semanalmente los hallazgos en `knowledge-base.md`.
