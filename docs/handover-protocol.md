# PROTOCOLO DE TRANSFERENCIA (HANDOVER PROTOCOL)

## 1. ESTÁNDAR DE TRANSFERENCIA
El Handover es el único mecanismo oficial para pasar el control entre agentes. Debe realizarse siempre en español.

## 2. ESTRUCTURA REQUERIDA
Todo handover debe incluir los siguientes seis campos:

1.  **IDENTIFICACIÓN:**
    - Emisor: [ID_AGENTE] -> Receptor: [ID_AGENTE]
2.  **ESTADO DE LA TAREA:**
    - [COMPLETA | PARCIAL | BLOQUEADA]
3.  **CONTEXTO MÍNIMO:**
    - Resumen ejecutivo de lo realizado. Por qué se entrega la tarea ahora.
4.  **ARCHIVOS AFECTADOS:**
    - Enlaces directos (Markdown) a archivos creados o modificados en `/projects` o `/memory`.
5.  **RIESGOS Y NOTAS:**
    - Advertencias sobre deudas técnicas, ambigüedades de requisitos o riesgos de seguridad detectados.
6.  **PRÓXIMA ACCIÓN SUGERIDA:**
    - Qué espera el emisor que el receptor haga a continuación.

## 3. VALIDACIÓN
El receptor debe confirmar la recepción validando que los archivos referenciados son legibles. Si falta información, el receptor tiene la obligación de solicitar aclaración al emisor antes de iniciar su fase de **EJECUCIÓN**.

---
*Referencia: standards/communication-standards.md*
