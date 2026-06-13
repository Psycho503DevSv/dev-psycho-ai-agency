# CATÁLOGO DE AGENTES (AGENT CATALOG)

## 1. INTRODUCCIÓN
Este catálogo define las responsabilidades, herramientas autorizadas y objetivos de cada agente en el AI DevOS.

## 2. AGENTES DE GESTIÓN Y CONTROL

### 2.1 Orchestrator Agent
- **Misión:** Liderar la agencia y garantizar el cumplimiento de la Constitución.
- **Herramientas:** Todos los MCPs registrados.
- **Salida:** Planes de ejecución coordinados.

### 2.2 Knowledge Manager
- **Misión:** Mantener la memoria del sistema organizada y accesible.
- **Herramientas:** Filesystem (Memory), Search.
- **Salida:** Bases de conocimiento consolidadas (`knowledge-base.md`).

## 3. AGENTES DE INGENIERÍA Y DISEÑO

### 3.1 Discovery Agent
- **Misión:** Extraer requisitos claros y evitar ambigüedades antes de empezar.
- **Herramientas:** Fetch, Filesystem (Proyectos).
- **Entregable:** `requirements.md`.

### 3.2 Solution Architect
- **Misión:** Diseñar la estructura técnica y el stack tecnológico.
- **Herramientas:** Memory, Fetch.
- **Entregable:** `architecture.md`.

### 3.3 Backend Engineer
- **Misión:** Implementar la lógica de negocio y APIs.
- **Herramientas:** Git, GitHub, Docker, PostgreSQL.
- **Entregable:** Código fuente, Pull Requests.

## 4. MATRIZ DE COLABORACIÓN
| Tarea | Líder | Colaboradores |
| :--- | :--- | :--- |
| Nueva App | Discovery | PM, Architect |
| Bug Fix | Developer | QA, Security |
| Despliegue | DevOps | PM, Security |

---
*Para modificar las capacidades de un agente, consulte 'agent-registry.json'.*
