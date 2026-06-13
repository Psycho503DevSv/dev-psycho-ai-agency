# PLANNING ENGINE: GESTIÓN DE RUTA CRÍTICA
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Gestionar la secuencia temporal y lógica de ejecución, optimizando recursos y garantizando que las dependencias críticas se resuelvan primero.

### 2. DETERMINACIÓN DE LA RUTA CRÍTICA (CPM)
El motor analiza las tareas atomizadas en el `task-decomposition-engine.md` y construye un grafo de dependencias:
- **Tareas Secuenciales (Serial):** Si la Tarea B requiere el output de la Tarea A.
- **Tareas Paralelas (Sync):** Si ambas tareas operan en dominios desconectados (ej. `docs/` y `css/`).
- **Milestones (Hitos):** Puntos de sincronización obligatoria donde todos los agentes se detienen para un Quality Gate global.

### 3. MATRIZ DE PRIORIZACIÓN DE PLANIFICACIÓN
| Prioridad | Criterio | Acción de Planificación |
| :--- | :---: | :--- |
| **P1 (Bloqueante)** | Infraestructura, DB Schema, Auth. | Ejecutar como primera tarea del sprint. |
| **P2 (Core)** | Lógica de negocio principal. | Ejecutar inmediatamente tras P1. |
| **P3 (UI/Estética)**| Frontend visual, estilos, docs menores. | Encolar para ejecución paralela suave. |
| **P4 (Refactor)** | Limpieza de código, comentarios. | Opcional, solo si sobra "Token Budget". |

### 4. REPLANIFICACIÓN DINÁMICA (RE-PLAN)
Si una tarea falla o el Usuario cambia el requisito:
1. **Invalidación de Rama:** Se marcan todas las tareas dependientes como `STALE`.
2. **Re-evaluación:** El motor calcula el camino más corto desde el estado actual al nuevo estado final.
3. **Notificación:** Se genera un nuevo `Roadmap Update` para que el resto de agentes ajusten su contexto.

### 5. CASO LÍMITE: "PLAN PARALYSIS"
- **Escenario:** El plan es tan complejo que genera 50 mini-tareas.
- **Solución:** El motor agrupa tareas por "Agente Destino" y las consolida en un único `Handover Package` de nivel superior.

### 6. EJEMPLO OPERATIVO
**Plan Original:** `Repo Setup` -> `DB Setup` -> `API Setup`.
**Detección de Riesgo:** `DB Setup` falla por falta de credenciales.
**Re-Plan:** Mover `Repo Setup` a `COMPLETED`. Pausar `DB Setup`. Activar `DevOps-Agent` para solicitar credenciales via Terminal.
