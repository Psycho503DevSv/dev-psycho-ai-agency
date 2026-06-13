# WORKFLOW: PROJECT PLANNING (PLANIFICACIÓN)

## 1. OBJETIVO
Diseñar la arquitectura técnica, seleccionar el stack y definir el roadmap detallado.

## 2. TRIGGER
Aprobación del `requirements.md` generado en el flujo de Descubrimiento.

## 3. AGENTES PARTICIPANTES
1.  **Orchestrator:** Coordinación.
2.  **Solution Architect:** Líder del flujo. Diseño de sistemas.
3.  **Project Manager:** Creación de roadmap e hitos.
4.  **Database Architect:** Diseño del esquema de datos.
5.  **AI Engineer:** Definición de integraciones de IA (si aplica).

## 4. FLUJO DE TRABAJO (HANDOVER)
1.  **Orchestrator -> Solution Architect:** Diseñar arquitectura basada en requisitos.
2.  **Solution Architect -> Database Architect:** Solicitar diseño de tablas y relaciones.
3.  **Database Architect -> Solution Architect:** Entrega de `schema.sql` y diagramas ER.
4.  **Solution Architect -> Project Manager:** Entregar planos para definición de tareas.
5.  **Project Manager -> Orchestrator:** Roadmap final y backlog listo para desarrollo.

## 5. INPUTS Y OUTPUTS
- **Inputs:** `requirements.md`, `standards/coding-standards.md`.
- **Outputs:** `architecture.md`, `roadmap.md`, `schema.sql`.

## 6. CRITERIOS DE ÉXITO Y RIESGOS
- **Éxito:** Arquitectura escalable aprobada por el Security Engineer.
- **Riesgo:** Selección de tecnologías incompatibles o excesivamente complejas.
- **Bloqueo:** Conflicto de diseño entre Architect y Database Architect.

---
*ID: wf-planning | Registro: registry/workflow-registry.json*
