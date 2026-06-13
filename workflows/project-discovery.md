# WORKFLOW: PROJECT DISCOVERY (DESCUBRIMIENTO)

## 1. OBJETIVO
Definir con precisión los requisitos, el alcance y la viabilidad del proyecto antes de asignar recursos técnicos.

## 2. TRIGGER
Solicitud del usuario para una nueva funcionalidad, aplicación o servicio.

## 3. AGENTES PARTICIPANTES
1.  **Orchestrator:** Supervisión y activación.
2.  **Discovery Agent:** Líder del flujo. Captura de requisitos.
3.  **Knowledge Manager:** Consulta de antecedentes en `/memory`.
4.  **Project Manager:** Estimación inicial de hitos.

## 4. FLUJO DE TRABAJO (HANDOVER)
1.  **Usuario -> Orchestrator:** Petición inicial.
2.  **Orchestrator -> Discovery Agent:** Iniciar entrevista de requisitos.
3.  **Discovery Agent -> Knowledge Manager:** ¿Hay proyectos similares en `/memory/lessons-learned/`?
4.  **Knowledge Manager -> Discovery Agent:** Reporte de antecedentes y riesgos pasados.
5.  **Discovery Agent -> Orchestrator:** Entrega de `requirements.md` final.

## 5. INPUTS Y OUTPUTS
- **Inputs:** Prompt del usuario, historial de `/memory`.
- **Outputs:** `requirements.md`, `project-vision.md`.

## 6. CRITERIOS DE ÉXITO Y RIESGOS
- **Éxito:** Requisitos 100% claros (sin ambigüedades técnicas).
- **Riesgo:** Alcance mal definido ("scope creep") desde el inicio.
- **Bloqueo:** El usuario no provee información suficiente tras 3 intentos.

---
*ID: wf-discovery | Registro: registry/workflow-registry.json*
