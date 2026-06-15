# Contributing to Psycho AI DevOS

Thank you for your interest in contributing to **Psycho AI DevOS**! We want to make it as easy and transparent as possible to contribute to this autonomous AI developer orchestration system.

---

## Code of Conduct

Please maintain a collaborative, respectful, and professional atmosphere when communicating with the community and maintainers.

## Code Conventions

1. **Python version**: We target Python 3.9 through 3.11.
2. **PEP 8 Guidelines**: Adhere to PEP 8 standards. Keep lines readable (recommended limit of 100 characters).
3. **Pydantic Schemas**: Any new data schema or state object must be declared in [schemas.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/runtime/schemas.py) using Pydantic V2 to enforce data validation.
4. **Logging**: Never use raw `print()` for runtime operations. Always use the unifed logging system from [logger.py](file:///c:/Users/kalin/OneDrive/Desktop/agente/runtime/logger.py).
5. **No Wildcard Permissions**: When adding command execution tools, enforce role-based command whitelist checks.

---

## Guide to Creating New Agents

Adding a new agent to the DevOS orchestra is simple:

1. **Create the Agent Directory**:
   Create a new folder inside the `agents/` folder: `agents/<agent-name>/`.
   
2. **Write Instructions**:
   Create an `instructions.md` file in `agents/<agent-name>/instructions.md` defining the agent's identity, system prompt, target capabilities, and behavior.

3. **Register Agent Actions**:
   If the agent requires special roles or permissions, register the role and define its command whitelist in the `mcp_executor.py` (`_check_role_permissions` whitelist).
   
4. **Update Workflow Registry**:
   To include this agent in existing or new workflows, update the JSON files in `registry/` (e.g. `mcp-registry.json` or workflow step lists).

---

## Testing & Coverage

We enforce a strict testing policy. All new features or refactors must include unit/integration tests.

- Run the test suite:
  ```bash
  pytest
  ```
- Generate a coverage report:
  ```bash
  pytest --cov=runtime --cov-report=html
  ```
- **Coverage threshold**: We maintain a minimum of **70% coverage** for code inside the `runtime/` package. Pull Requests that drop the total coverage below this threshold will fail the CI check.
