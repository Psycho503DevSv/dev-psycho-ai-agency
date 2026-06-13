# WORKFLOW SELECTION ENGINE: TOPOLOGÍA DE EQUIPO
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Determinar la estructura óptima de ejecución (Secuencial, Paralela o Híbrida) y seleccionar el set de agentes necesarios para un objetivo dado.

### 2. MATRIZ DE TOPOLOGÍAS
| Topología | Cuándo Usar | Configuración de Agentes |
| :--- | :--- | :--- |
| **Pipeline (Secuencial)** | Tareas con dependencias fuertes (ej. Diseñar -> Codificar -> Testear). | A $\rightarrow$ B $\rightarrow$ C. |
| **Swarm (Paralelo)** | Tareas independientes masivas (ej. Crear 10 componentes de UI). | A + B + C simultáneos. |
| **Iterative (Bucle)** | Tareas de optimización o bug-hunting. | A $\leftrightarrow$ B hasta éxito. |
| **Audited (Supervisado)** | Tareas críticas de seguridad o infraestructura. | Executor + Auditor (Reviewer). |

### 3. CRITERIOS DE SELECCIÓN DE AGENTES
El motor consulta el `agent-registry.json` y aplica filtros:
1. **Disponibilidad:** ¿El agente está `IDLE`?
2. **Context Fit:** ¿El agente tiene cargado el contexto técnico necesario?
3. **Specialty Score:** Ver `agent-scoring-engine.md` para el dominio específico.

### 4. REGLAL DE LIMITE DE EQUIPO (ANTI-CHAOS)
- Máximo 3 agentes trabajando en paralelo para evitar conflictos de git merge o saturación de tokens del sistema operativo.
- El Orchestrator siempre actúa como el "Sincronizador" al final de cada fase paralela.

### 5. EJEMPLO OPERATIVO
**Requisito:** "Audita la seguridad de la API y corrígela".
**Selección:** 
- **Topología:** Audited (Secuencial).
- **Agentes:** Security-Engineer (Audit) $\rightarrow$ Backend-Engineer (Fix) $\rightarrow$ Security-Engineer (Verification).
