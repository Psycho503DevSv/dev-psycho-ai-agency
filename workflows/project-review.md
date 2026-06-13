# WORKFLOW: PROJECT REVIEW (REVISIÓN)

## 1. OBJETIVO
Validar la calidad, seguridad y funcionamiento del código antes del lanzamiento.

## 2. TRIGGER
Pull Request (PR) o marcación de tarea como "Finalizada" por los ingenieros.

## 3. AGENTES PARTICIPANTES
1.  **Security Engineer:** Auditoría de vulnerabilidades.
2.  **QA Engineer:** Testing E2E y funcional.
3.  **Code Reviewer:** Calidad técnica y deuda técnica.
4.  **Documentation Engineer:** Verificación de docs actualizados.

## 4. FLUJO DE TRABAJO (HANDOVER)
1.  **Orchestrator -> Code Reviewer:** Validar estándares de codificación.
2.  **Code Reviewer -> Security Engineer:** Si el código es limpio, auditar seguridad.
3.  **Security Engineer -> QA Agent:** Si es seguro, ejecutar suites de tests.
4.  **QA Agent -> Documentation Specialist:** Si funciona, actualizar manuales.

## 5. INPUTS Y OUTPUTS
- **Inputs:** Código en el repositorio, `architecture.md`.
- **Outputs:** Reporte de QA, Auditoría de Seguridad, Documentación de API.

## 6. CRITERIOS DE ÉXITO Y RIESGOS
- **Éxito:** Cero vulnerabilidades críticas detectadas y tests pasados al 100%.
- **Riesgo:** Cuello de botella en la revisión de seguridad.

---
*ID: wf-review | Registro: registry/workflow-registry.json*
