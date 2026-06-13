# PLANTILLA DE WORKFLOW (FLUJO DE TRABAJO)

## 1. DEFINICION
**Nombre:** {{WF_NAME}}
**ID:** `wf-{{WF_ID}}`
**Trigger:** {{EVENT_TRIGGER}}

## 2. SECUENCIA DE PASOS (REFERENCIA AGENTES)
1. **Paso 1:** {{AGENT_ID_1}} -> Realiza [Accion]
2. **Paso 2:** {{AGENT_ID_2}} -> Valida [Resultado]

## 3. EJEMPLO REAL: FLUJO DE DOCUMENTACION
1. **Developer:** Finaliza codigo y actualiza README parcial.
2. **Documentation Agent:** Procesa cambios y genera CHANGELOG.md.
3. **Git Manager:** Crea el commit con los docs actualizados.
