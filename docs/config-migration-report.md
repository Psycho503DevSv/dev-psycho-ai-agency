# Config Migration Report

Centralized settings has been introduced at [settings.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/config/settings.py). All hardcoded runtime and tools paths have been migrated to use this centralized config.

## Relocated Configurations

| Variable Name | Description | Target Value / Path |
| :--- | :--- | :--- |
| `BASE_DIR` | Project root directory | Determined dynamically |
| `REGISTRY_DIR` | Registry folder path | `BASE_DIR/registry` |
| `AGENT_REGISTRY` | Agent registry JSON path | `REGISTRY_DIR/agent-registry.json` |
| `WORKFLOW_REGISTRY` | Workflow registry JSON path | `REGISTRY_DIR/workflow-registry.json` |
| `MCP_REGISTRY` | MCP registry JSON path | `REGISTRY_DIR/mcp-registry.json` |
| `PROJECTS_DIR` | Projects workspace path | `BASE_DIR/projects` |
| `RUNTIME_DIR` | Core runtime path | `BASE_DIR/runtime` |
| `AGENTS_DIR` | Agents definitions folder | `BASE_DIR/agents` |
| `DOCS_DIR` | Report and documentation directory | `BASE_DIR/docs` |
| `MEMORY_DIR` | Memory storage parent path | `BASE_DIR/memory` |
| `SESSIONS_DIR` | User memory sessions storage | `MEMORY_DIR/sessions` |
| `PATTERNS_DIR` | Promoted global patterns storage | `MEMORY_DIR/patterns` |

## Refactored Files

The following files have been modified to completely remove hardcoded paths and rely exclusively on [settings.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/config/settings.py):

1. [runtime/agent_loader.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/runtime/agent_loader.py)
2. [runtime/memory_engine.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/runtime/memory_engine.py)
3. [runtime/workflow_runner.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/runtime/workflow_runner.py)
4. [tools/health-check.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/tools/health-check.py)
5. [tools/mcp_diagnostics.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/tools/mcp_diagnostics.py)
6. [tools/mcp_healthcheck.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/tools/mcp_healthcheck.py)
7. [tools/mcp_installer.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/tools/mcp_installer.py)
8. [tools/validate-registry.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/tools/validate-registry.py)

## Validation Status

- All files verified to correctly import `config.settings`.
- No lingering hardcoded string paths inside the core `runtime/` engine.
