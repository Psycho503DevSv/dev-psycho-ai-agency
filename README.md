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

Dependencies are minimal. Ensure you have Python installed:

```bash
pip install -r requirements.txt
```

---

## 📄 License

This project is open-source and available under the MIT License.
