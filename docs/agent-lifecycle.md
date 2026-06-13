# CICLO DE VIDA DEL AGENTE (AGENT LIFECYCLE)

## 1. ESTADOS DEL AGENTE
Todo agente en el AI DevOS debe transitar por los siguientes estados definidos en el `agent-registry.json`:

1.  **CREACIÓN (OFFLINE):** El agente existe como `.instructions.md` pero no está registrado ni activo.
2.  **ACTIVACIÓN (READY):** El agente está registrado y el Orchestrator ha verificado su disponibilidad.
3.  **EJECUCIÓN (BUSY):** El agente está procesando una tarea y tiene bloqueado su contexto actual.
4.  **SUSPENSIÓN (PAUSED):** El agente ha detenido su ejecución por falta de información o por orden del Orchestrator.
5.  **ERROR (FAILED):** El agente ha detectado una falla crítica o una alucinación. Requiere intervención del Security Engineer o Usuario.
6.  **RECUPERACIÓN (RECOVERY):** Proceso automático o manual para restaurar el estado "READY" tras un error.
7.  **RETIRO (DEPRECATED):** El agente es marcado como obsoleto y sus funciones son asumidas por una nueva versión.

## 2. TRANSICIONES OBLIGATORIAS
- **De READY a BUSY:** Solo mediante una instrucción formal del Orchestrator.
- **De BUSY a READY:** Solo tras completar el `Handover Protocol` y registrar la decisión en la memoria.
- **De BUSY a FAILED:** Disparado por el agente ante una excepción técnica o violación de la Constitución.

## 3. PROTOCOLO DE RECUPERACIÓN
Ante un estado de **ERROR**:
1. El agente debe volcar su contexto actual en `memory/sessions/error-logs/`.
2. El Orchestrator intenta un "Soft Reset" re-leyendo las instrucciones.
3. Si el error persiste, se escala al AI Engineer para revisión de prompts.
