# Architecture Overview

## Multi-Agent Orchestration Flow
- **Orchestrator:** `psycho-ceo` coordinates assignments.
- **State Management:** `memory/active_context.md` holds current sprint details.
- **Validation:** `agent-evaluator` parses agent outputs before finalizing workflows.
