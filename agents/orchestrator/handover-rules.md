# HANDOVER RULES: PROTOCOLO DE ESTADO (v2.0)
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Definir el estándar de oro para la transferencia de conocimiento entre el Orchestrator y los Agentes Especialistas, eliminando la pérdida de contexto.

### 2. EL CONTRATO DE HANDOVER (ESTRUCTURA OBLIGATORIA)
Todo handover debe ser un bloque estructurado (XML o Markdown) con:

```markdown
### [TASK_ID] - [AGENT_ID]
**1. MISSION:** [Un solo objetivo ejecutable]
**2. STATE_OF_ART:** [Archivos creados, rutas de terminal, variables activas]
**3. CONTEXT_FILES:**
- [file_a](path/a)
- [file_b](path/b)
**4. CONSTRAINTS:** [Ej. "No modificar package.json", "No usar libs externas"]
**5. TERMINATION_CONTINGENCY:** [Qué hacer si falla la herramienta principal]
```

### 3. VALIDACIÓN DE ENTRADA (AGENT ACK)
Al recibir un handover, el agente receptor debe confirmar:
1. ¿Tengo acceso a todos los `CONTEXT_FILES`?
2. ¿Entiendo la `MISSION`?
3. ¿Mi `Capability-Matrix` cubre esta tarea?
Si alguna es NO, el agente debe devolver un `REJECT_HANDOVER` con el motivo.

### 4. PROTOCOLO DE RETORNO (HANDBACK)
El reporte de fin de tarea del especialista debe alimentar al `agent-scoring-engine.md`:
- **Artifacts:** Lista exacta de cambios realizados.
- **Log de Terminal:** Salida cruda de los últimos comandos técnicos.
- **Propuesta de Siguiente Paso:** Basado en los hallazgos técnicos.

### 5. CASOS DE BORDE
- **Handover Gigante:** El contexto pesa > 80% de la ventana del receptor.
    - *Acción:* El Orchestrator debe usar `context-management.md` para resumir antes de enviar.
- **Pérdida de Agente:** Un agente "muere" (timeout o error 404) en medio de un handover.
    - *Acción:* El Orchestrator recupera el `context-payload` del mensaje de salida y busca un sustituto.

### 6. EJEMPLO OPERATIVO
**De Orchestrator a Frontend:**
"Misión: Implementar el botón de Logout. Archivos: `App.js`, `Header.js`. Restricciones: No usar Redux, usa Context API. Si falla la compilación, revierte cambios en `Header.js`."
