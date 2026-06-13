# WORKFLOW: PROJECT RELEASE (LANZAMIENTO)

## 1. OBJETIVO
Desplegar la solución en el entorno de producción y cerrar oficialmente la fase de desarrollo.

## 2. TRIGGER
Aprobación final del flujo de Revisión.

## 3. AGENTES PARTICIPANTES
1.  **Git Manager:** Gestión de tags, branches y merges a `main`.
2.  **DevOps Engineer:** Despliegue (Docker, Cloudflare, etc.).
3.  **Project Manager:** Notificación de cierre de hito.
4.  **Knowledge Manager:** Extracción de lecciones finales.

## 4. FLUJO DE TRABAJO (HANDOVER)
1.  **Orchestrator -> Git Manager:** Realizar merge y crear Tag de versión.
2.  **Git Manager -> DevOps:** Ejecutar pipeline de despliegue.
3.  **DevOps -> Project Manager:** Confirmar disponibilidad del sistema.
4.  **Project Manager -> Knowledge Manager:** Solicitar consolidación de memoria.

## 5. INPUTS Y OUTPUTS
- **Inputs:** Código aprobado, credenciales de entorno.
- **Outputs:** Aplicación en vivo, `CHANGELOG.md` actualizado, `lessons-learned.md` poblado.

## 6. CRITERIOS DE ÉXITO
- Despliegue exitoso sin tiempo de inactividad (Zero downtime).
- Memoria persistente actualizada con la nueva versión.

---
*ID: wf-release | Registro: registry/workflow-registry.json*
