# WORKFLOW: PROJECT MAINTENANCE (MANTENIMIENTO)

## 1. OBJETIVO
Atender bugs, realizar actualizaciones de seguridad y optimizar el rendimiento post-lanzamiento.

## 2. TRIGGER
Reporte de error (Bug Report), vulnerabilidad detectada o solicitud de optimización.

## 3. AGENTES PARTICIPANTES
1.  **Support Agent:** Atención y triage inicial.
2.  **QA Engineer:** Reproducción del fallo.
3.  **Security Engineer:** Triage de vulnerabilidades.
4.  **Developer Agent:** Resolución técnica.

## 4. FLUJO DE TRABAJO
1.  **Usuario -> Support:** Reporte de incidencia.
2.  **Support -> QA:** Validar y documentar pasos de reproducción.
3.  **QA -> Developer:** Asignar corrección.
4.  **Developer -> Review Workflow:** (Lanza el flujo de revisión antes de subir la mejora).

## 5. CRITERIOS DE ÉXITO
- SLA de respuesta cumplido.
- Regresión evitada mediante tests.

---
*ID: wf-maintenance | Registro: registry/workflow-registry.json*
