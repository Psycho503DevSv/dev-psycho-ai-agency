# DECISION ENGINE: ALGORITMO DE RUTA 5D
## AI DevOS Orchestrator Module

### 1. MODELO DE DECISIÓN MULTIVARIABLE
El Orchestrator asigna tareas utilizando una función de conveniencia $f(A, T, R, L, H) \rightarrow S$ donde:
- **A (Agent Capabilities):** Match de habilidades en el registry.
- **T (Trust Score):** Reputación histórica del agente.
- **R (Risk Impact):** Nivel de riesgo de la tarea.
- **L (Load Factor):** Carga actual de tokens/memoria del agente.
- **H (History):** Éxito previo en tareas idénticas.

### 2. MATRIZ DE RATING DE AGENTES
| Criterio | Peso | Valoración | Acción si es Bajo |
| :--- | :---: | :--- | :--- |
| **Capacidad** | 40% | ¿Tiene la herramienta MCP necesaria? | Buscar sustituto o denegar. |
| **Confianza** | 20% | Score de `agent-scoring-engine.md`. | Forzar validación humana. |
| **Carga** | 10% | < 70% de uso de contexto. | Encolar tarea. |
| **Historial** | 20% | Casos similares resueltos con éxito. | Asignación con tutoría del Orch. |
| **Riesgo** | 10% | Impacto si la tarea falla. | Solo agentes `Level: Admin`. |

### 3. ÁRBOL DE DECISIÓN (ROUTING)
1. ¿La tarea toca archivos de configuración del sistema?
   - **SÍ:** ¿Usuario confirmó? No $\rightarrow$ Bloquear. Sí $\rightarrow$ Orchestrator ejecuta.
2. ¿La tarea requiere acceso a internet?
   - **SÍ:** ¿Está permitido en `standards/constitution.md`? No $\rightarrow$ Error. Sí $\rightarrow$ Inyectar `Fetch-Agent`.
3. ¿Es una tarea de refactorización pura?
   - **SÍ:** Evaluar Trust Score del `AI-Engineer`. > 0.85 $\rightarrow$ Delegar. < 0.85 $\rightarrow$ Dividir en tasks pequeñas.

### 4. CASOS LÍMITE (EDGE CASES)
- **Deadlock de Agentes:** Dos agentes se bloquean esperando el output del otro. 
    - *Solución:* El Orchestrator corta la ejecución, toma el contexto de ambos y resuelve la inconsistencia manualmente mediante el `conflict-resolution-engine.md`.
- **Alucinación Persistente:** Un agente asegura haber hecho algo que el Orchestrator no detecta en el FS.
    - *Solución:* Marcar al agente con `Doubt-Flag`, ejecutar `ls` forzado y bajar su Trust Score en -0.2.

### 5. EJEMPLO DE HANDOVER BASADO EN DECISIÓN
**Decisión:** Delegar a `Security-Agent` por alto riesgo en manejo de secrets.
**Racional:** Tarea nivel 5. Trust del AI-Engineer en criptografía es bajo (0.4).
**Comando:** `EXECUTE flow-security-audit path=/src/auth`
