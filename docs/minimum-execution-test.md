# TEST DE EJECUCIÓN MÍNIMA: JSON TO CSV CONVERTER

## 1. DEFINICIÓN DEL PROYECTO DE PRUEBA
- **Nombre:** `json-csv-mini`
- **Funcionalidad:** Script Python que lee `input.json` y genera `output.csv`.
- **Objetivo de Prueba:** Validar el traspaso de contexto entre Orchestrator -> PM -> AI Engineer -> Knowledge Manager.

## 2. SIMULACIÓN DE WORKFLOW (EVIDENCIA DE CAMPO)

### FASE 1: DISCOVERY (Orchestrator + Knowledge Manager)
- **Acción:** Definición de requerimientos técnicos.
- **Input:** "Crear un conversor JSON a CSV en Python".
- **Archivos Utilizados:** `registry/workflow-registry.json` (ID: `wf-discovery`).
- **MCP Utilizado:** `filesystem` (lectura de estándares).
- **Riesgo:** ¿Están los estándares de Python definidos?
- **Estado:** PASS.

### FASE 2: PLANNING (Orchestrator + Project Manager)
- **Acción:** Creación de roadmap de tareas.
- **Input:** Requerimientos de Fase 1.
- **Outputs Tentativos:** `docs/architecture.md`, `projects/json-csv-mini/roadmap.md`.
- **Riesgo:** El Project Manager referencia un `roadmap.md` que debe ser creado físicamente.
- **Estado:** PASS (Si se crea el archivo).

### FASE 3: IMPLEMENTATION (AI Engineer)
- **Acción:** Escritura del código.
- **Input:** `roadmap.md` + Guía de Estilo.
- **Archivos a Crear:** `projects/json-csv-mini/converter.py`.
- **MCP Sugerido:** `filesystem` + `terminal`.
- **Estado:** PENDING (Requiere ejecución).

### FASE 4: KNOWLEDGE CAPTURE (Knowledge Manager)
- **Acción:** Registro de lecciones aprendidas.
- **Input:** Resultado de la implementación.
- **Archivos Utilizados:** `memory/sessions/`.
- **Estado:** PENDING.

## 3. VERIFICACIÓN DE CADENA CORE
- [ ] **Orchestrator:** Existe en `agents/orchestrator/`.
- [ ] **Project Manager:** Existe en `agents/project-manager/`.
- [ ] **AI Engineer:** Existe en `agents/ai-engineer/`.
- [ ] **Knowledge Manager:** Existe en `agents/knowledge-manager/`.
