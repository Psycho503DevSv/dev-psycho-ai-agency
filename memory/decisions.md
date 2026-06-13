# Architecture Decisions Log (ADR)

## ADR 001: Transition to Multi-Agent Platform (Psycho Agency)
- **Status:** Approved
- **Context:** Previous design acted as a prompt library rather than an active multi-agent system.
- **Decision:** Restructure agent registry and loaders to use `psycho-ceo` as the entry orchestrator and specialized engineers for functional units.
- **Consequences:** Clear role delegation and context optimization.
