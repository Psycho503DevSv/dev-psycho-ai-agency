# MOTOR DE DECISIÓN DEL ORQUESTADOR (ORCHESTRATOR DECISION ENGINE)

## 1. LÓGICA DE SELECCIÓN DE AGENTES
El Orchestrator selecciona agentes basándose en:
1.  **Competencia:** Match entre los `capabilities` del `agent-registry.json` y la tarea.
2.  **Estado:** Solo selecciona agentes en estado `READY`.
3.  **Jerarquía:** Nivel de autoridad requerido para la tarea.

## 2. SELECCIÓN DE WORKFLOWS Y MCPs
- **Workflows:** Si la entrada del usuario coincide con un `trigger` en `registry/workflow-registry.json`, se inicia la secuencia automática.
- **MCPs:** Se asignan herramientas basándose exclusivamente en la `MCP Capability Matrix`. El Orchestrator bloquea cualquier intento de un agente de usar una herramienta no autorizada.

## 3. RESOLUCIÓN DE CONFLICTOS Y BLOQUEOS
- **Conflicto de Reglas:** Aplica la jerarquía de la Constitución (Nivel 1 > Nivel 5).
- **Conflictos entre Agentes:** El Orchestrator actúa como árbitro final. Si la discrepancia es técnica, consulta al AI Engineer o Solution Architect.
- **Detección de Bloqueos:** Si un agente no produce un output en el tiempo esperado o solicita la misma información repetidamente, el Orchestrator interviene para re-evaluar el plan.

---
*Referencia: agents/orchestrator/instructions.md*
