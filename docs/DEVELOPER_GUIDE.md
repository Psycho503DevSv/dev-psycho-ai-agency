# Developer Guide — Psycho AI DevOS Architecture & Runtime Flow

Welcome to the Developer Guide. This document explains the internal mechanisms, architecture components, and execution flows of the **Psycho AI DevOS** agentic system.

---

## 1. System Architecture Overview

Psycho AI DevOS is a multi-agent framework designed to orchestrate software development tasks using autonomous AI agents equipped with Model Context Protocol (MCP) tools, RAG memory, and automated quality gating.

```mermaid
graph TD
    User([User Request / CLI]) --> Runner[Workflow Runner]
    Runner --> Loader[Agent Loader]
    Runner --> Memory[Memory Engine / Graphiti]
    Runner --> MCP[MCP Executor]
    Runner --> Dashboard[Observability Dashboard]
    MCP --> Command[Local / Sandbox Command execution]
    Runner --> Quality[Quality Gate / Tests]
```

---

## 2. Core Components

### 2.1. Workflow Runner (`runtime/workflow_runner.py`)
The orchestrator that loads the workflow registry, instantiates step execution, and runs the agent loop. It coordinates failover between NVIDIA NIM models and OpenAI GPT models, manages token cost estimations, and ensures graceful shutdown by saving state to `memory/interrupted_state.json` on `SIGINT`/`SIGTERM`.

### 2.2. Agent Loader (`runtime/agent_loader.py`)
Loads instructions, credentials, and identity definitions from individual `agents/` directories.

### 2.3. Memory Engine (`runtime/memory_engine.py` & `runtime/graphiti_bridge.py`)
Provides semantic recall and pattern storage.
- If Neo4j credentials and Graphiti API keys are present, it uses `Graphiti` to build dynamic episodic graph networks of lessons learned.
- If Graphiti is disabled, it transparently falls back to local JSON-based structured pattern storage.

### 2.4. MCP Executor (`runtime/mcp_executor.py`)
Executes tools (such as reading/writing files, listing directories, and running commands). Enforces strict path validation (`_resolve_path`) within the workspace boundary and performs role-based command whitelist checks to prevent unauthorized scripts from executing.

### 2.5. Quality Gate (`runtime/quality_gate.py`)
Runs automated checks (syntactic verification, bandit security checks, unit testing) on generated projects before marking workflows as successful.

### 2.6. Observability Dashboard (`runtime/dashboard.py`)
Runs a background multi-threaded HTTP server (default port `8050`). It collects real-time metrics, processes `ask_user` prompts dynamically from the Web UI, exposes workflow progress nodes, and outputs formatted color-coded agent logs.

---

## 3. The Runtime Loop Step-by-Step

When a workflow runs:
1. **Initialize State**: The `WorkflowRunner` spins up the background `Dashboard` server.
2. **Execute Steps**: For each agent step in the workflow definition:
   - Load agent context and system prompts.
   - Run the agent loop: query the LLM with context compressed dynamically by `ContextCompressor`.
   - Parse tool calls. If the agent makes a tool call, the `McpExecutor` validates its safety (role-based command checks and folder confinement).
   - If the tool is `ask_user`, execution halts, setting a `pending_question` on the dashboard, and waits until a response is typed in the CLI or submitted via the web interface.
   - Save the outcome of the step in the `MemoryEngine`.
3. **Quality Gating**: Once steps finish, the `QualityGate` evaluates the project workspace.
4. **Auto-Learning**: The `AutoLearner` parses execution details and logs, updating the global `lessons_learned.md` registry with tips for future workflows.

---

## 4. Multi-PC Deployment & Hybrid Workflow

To successfully run and deploy Psycho AI DevOS across multiple environments, it is critical to understand the separation of responsibilities:

### 4.1. The Hybrid Workflow Model
* **The DevOS Agent is the Orchestrator, Quality Gate, and Auto-Trainer:**
  * It sequences steps and agents.
  * It runs checks, security audits, and verifies code compilation.
  * It auto-trains itself via the **AutoLearner** using API keys (`.env`) to read session logs and write `memory/lessons_learned.md`.
  * It does NOT write the bulk of code or design from scratch; it coordinates and validates.
* **The Coding is Done by the Developer IDE / Local AI:**
  * Writing code, styling, and premium features are produced by your development environments (e.g., Antigravity, OpenCode, Claude, or Gemini CLI).
  * This hybrid approach maximizes code quality, minimizes token usage, and guarantees autonomous quality gating.

### 4.2. Setting Up on a New PC
Follow these steps to deploy on any new machine:
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Psycho503DevSv/dev-psycho-ai-agency.git
   cd dev-psycho-ai-agency
   ```
2. **Run the One-Click Setup Script** (PowerShell on Windows):
   ```powershell
   .\install.ps1
   ```
   *This script will create the virtual environment, upgrade pip, install all production & testing dependencies, set up a template `.env` if none exists, and run the test suite to verify the setup is healthy.*
3. **Configure Environment Keys**:
   Edit the generated `.env` file and set up your API keys:
   ```env
   OPENAI_API_KEY=your_openai_key
   NVIDIA_API_KEY=your_nvidia_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ```
4. **Access the Real-time Observability Dashboard**:
   Open your browser at `http://localhost:8050` to view active logs, task statuses, and interact with the agents' `ask_user` prompts.
5. **Run the System**:
   Execute workflows using Python:
   ```powershell
   .venv\Scripts\python.exe setup.py --run
   ```
   Or run the workflow runner directly:
   ```powershell
   .venv\Scripts\python.exe -m runtime.workflow_runner wf-build-project my-app-name
   ```
