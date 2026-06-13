# TOOL SELECTION ENGINE: RACIONAL DE RECURSOS
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Seleccionar la herramienta MCP óptima para cada tarea basándose en criterios de precisión, velocidad, riesgo y coste de contexto.

### 2. CRITERIOS DE SELECCIÓN
El motor evalúa las herramientas disponibles en el entorno contra la necesidad actual:

| Necesidad | Herramienta Primaria | Fallback (Si falla la 1ra) | Motivo de Fallback |
| :--- | :--- | :--- | :--- |
| Búsqueda de Código | `grep_search` | `semantic_search` | Precisión vs Contexto. |
| Lectura de Archivo | `read_file` | `run_in_terminal(cat)`| Disponibilidad de API. |
| Gestión de Entorno | `run_in_terminal` | - | Es la herramienta definitiva. |
| Validación Visual | `screenshot_page` | `read_page` | Necesidad de CSS vs HTML. |

### 3. OPTIMIZACIÓN DE COSTE (TOKEN BUDGET)
- **No usar `semantic_search`** si el archivo objetivo es conocido; usar `read_file` directo.
- **No usar `list_dir` recursivo** en repositorios gigantes; usar `file_search` con patrones específicos.
- **Evitar multi-calls:** Si se requieren 3 lecturas, ejecutarlas en paralelo en el mismo turno si el modelo lo soporta.

### 4. REGLAS DE SEGURIDAD EN SELECCIÓN
1. PROHIBIDO usar herramientas que requieran `sudo` sin aviso.
2. PROHIBIDO usar herramientas de red fuera de los dominios autorizados en `standards/constitution.md`.
3. Herramientas destructivas (Git reset, Docker kill) siempre se seleccionan como ÚLTIMA opción.

### 5. CASO DE ERROR: "TOOL UNAVAILABLE"
Si el Host deshabilita un MCP (ej. desactivan Playwright):
- El motor marca la herramienta como `OFFLINE` en el internal registry.
- Busca un flujo alternativo (ej. Inspección manual de logs en lugar de visualización del navegador).
- Si no hay alternativa, reporta `ERR_TOOLCHAIN_BROKEN`.
