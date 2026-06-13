# CONTEXT MANAGEMENT: OPTIMIZACIÓN DE WINDOW
## AI DevOS Orchestrator Module

### 1. ALGORITMO DE PODA (CONTEXT PRUNING)
El Orchestrator monitoriza el `Context_Usage`. Si > 80%, aplica el siguiente protocolo de emergencia:

#### Paso 1: Identificación de Ruido (Entropy Reduction)
- Quitar bloques de código que no han sido editados en los últimos 2 turnos.
- Reemplazar funciones largas por su "Signature" (definición sin cuerpo).
- Eliminar mensajes de confirmación ("Entendido", "Ok").

#### Paso 2: Compresión de Estado (Check-pointing)
- Generar un archivo `memories/session/checkpoint.md` con el estado actual del Roadmap.
- Re-inicializar la conversación cargando solo la Constitución + Checkpoint + Tarea Actual.

### 2. MATRIZ DE PRIORIDAD DE TOKENS
| Prioridad | Tipo de Información | Acción del Puning |
| :--- | :--- | :--- |
| **P1 (Crítica)** | Requisito actual + Constitución. | Inamovible. |
| **P2 (Alta)** | Roadmap + Código en edición inmediata. | Mantener completo. |
| **P3 (Media)** | Memoria de la sesión + Logs recientes. | Resumir/Truncar. |
| **P4 (Baja)** | Saludos, intro, agradecimientos, docs generales. | Borrado agresivo. |

### 3. PROTOCOLO DE LECTURA (SELECTIVE INTAKE)
- Antes de leer un archivo de >200 líneas, ejecutar `grep_search` para identificar el bloque relevante.
- Usar `read_file` solo para los rangos detectados (L10-L40, etc.).

### 4. CASO LÍMITE: "LOST IN THE MIDDLE"
Si el contexto es muy denso, el LLM tiende a ignorar el centro de la ventana.
- **Acción Orchestrator:** Repetir los requisitos más críticos al FINAL del prompt de sistema en cada turno técnico para reforzar la atención.

### 5. EJEMPLO OPERATIVO
**Antes:** Contexto lleno de 15 archivos de diseño y 3 logs de error previos. (Total 10k tokens).
**Acción:** 
1. Resumir los 15 archivos en una tabla de arquitectura.
2. Quitar los logs de errores ya resueltos.
**Resultado:** Contexto reducido a 2k tokens con 100% de la información operativa necesaria preservada.
