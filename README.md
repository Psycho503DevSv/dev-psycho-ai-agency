# Personal AI DevOS v1 🚀

An agent-based virtual development agency ecosystem designed to coordinate, design, develop, test, and document software projects using LLM-based agents. 

Compatible with advanced developer environments like Antigravity, OpenCode, VS Code, and various LLM APIs (Gemini, Claude, GPT, Grok, Qwen).

---

## 🎯 Goal

Create a robust ecosystem of agents, standards, MCPs, and workflows capable of developing:
- 🌐 Web Apps
- 📱 Android APKs
- 🖥️ Desktop Applications (`.exe`)
- 🔌 REST & GraphQL APIs
- ☁️ SaaS Platforms
- 🛠️ Internal Tools

---

## 🏛️ Core Principles

### Regla #1: No Immediate Coding 🧠
No agent writes code immediately. The flow always requires:
1. Requirements Analysis
2. Documentation Review
3. Architecture Validation
4. Risk Detection
5. Implementation Planning
6. Coding & Execution

### Regla #2: Document Decisions 📝
All critical architectural and design decisions must be documented.

### Regla #3: Document Changes 🔄
Every codebase modification must update the corresponding documentation.

### Regla #4: Maintainability First 🛠️
Every feature must be implemented with future maintainability and readability in mind.

---

## 📁 Project Structure

```text
├── agents/          # Specialized agent prompts and logic
├── config/          # Configurations and environment settings
├── docs/            # Architecture, security, and UI standards
├── mcps/            # Model Context Protocol servers and integrations
├── memory/          # Long-term agent memory engines
├── projects/        # Workspace directories for active projects
├── registry/        # Registers of tools, agents, and templates
├── runtime/         # Orchestration kernel and runtime processes
├── standards/       # Style guides (Coding, UI/UX, Security)
├── templates/       # Templates for code, documentation, and tasks
├── tools/           # Custom helper tools and scripts
└── workflows/       # Predefined multi-agent execution workflows
```

---

## ⚙️ Requirements & Installation

Asegúrate de tener Python instalado y ejecuta:

```bash
pip install -r requirements.txt
```

---

## 🧠 Memory Management (Gestión de Memoria)

El sistema soporta dos modos de almacenamiento de memoria central:

1. **Modo Local (Por defecto):** Guarda la memoria en archivos JSON dentro del directorio local `memory/sessions/`. Es 100% gratuito y privado.
2. **Modo Grafo Semántico (Graphiti + Neo4j):** Si deseas usar una base de datos de grafos para relacionar conceptos de forma avanzada, puedes configurar un archivo `.env` en la raíz con las siguientes variables:
   ```ini
   USE_GRAPHITI=true
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=tu_contraseña
   OPENAI_API_KEY=tu_api_key_de_openai
   ```

---

## 🚀 Quick Start (Inicio Rápido)

### Ejecutar un Workflow de Agentes
Puedes correr flujos de trabajo predefinidos usando el `workflow_runner.py`:

```bash
python runtime/workflow_runner.py [workflow_id] [project_name]
```

*Ejemplo:*
```bash
python runtime/workflow_runner.py wf-discovery mi-proyecto-web
```

---

## 🧪 Testing (Ejecución de Pruebas)

Para correr las pruebas unitarias y verificar el correcto funcionamiento de los cargadores de agentes y motores de memoria:

```bash
python -m unittest tests/runtime/test_agent_loader.py
python -m unittest tests/runtime/test_graphiti_memory.py
```

---

## 📄 License

Este proyecto es de código abierto bajo la Licencia MIT.
