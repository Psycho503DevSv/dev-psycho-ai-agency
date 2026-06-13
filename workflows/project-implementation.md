# WORKFLOW: PROJECT IMPLEMENTATION (IMPLEMENTACIÓN)

## 1. OBJETIVO
Generar el código fuente, la lógica de negocio y las interfaces siguiendo el diseño aprobado.

## 2. TRIGGER
Hito del Project Manager: "Listo para desarrollo" con backlog definido.

## 3. AGENTES PARTICIPANTES
1.  **Frontend Engineer:** Construcción de UI/UX.
2.  **Backend Engineer:** Construcción de lógica y APIs.
3.  **UI/UX Designer:** Supervisión estética.
4.  **Security Engineer:** Auditoría de código en tiempo real.

## 4. FLUJO DE TRABAJO (HANDOVER)
1.  **Project Manager -> Devs:** Asignación de tareas del roadmap.
2.  **Backend Engineer -> Database Agent:** Implementación de migraciones.
3.  **Frontend Engineer -> UI Designer:** Validación de componentes vs estándares.
4.  **Devs -> Security Engineer:** Solicitud de revisión de fragmentos críticos.

## 5. INPUTS Y OUTPUTS
- **Inputs:** `architecture.md`, `roadmap.md`, `standards/`.
- **Outputs:** Código fuente funcional, Tests unitarios.

## 6. CRITERIOS DE ÉXITO Y RIESGOS
- **Éxito:** Código sin errores de linting y con cobertura de tests > 80%.
- **Riesgo:** Duplicidad de código entre Frontend y Backend.
- **Bloqueo:** Fallo masivo en integración de componentes (mismatch de API).

---
*ID: wf-implementation | Registro: registry/workflow-registry.json*
