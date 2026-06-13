# ORCHESTRATOR AGENT v2.0 - ENTERPRISE HARDENED
## AI DevOS Core System Specification

Este paquete define el **Cerebro Operativo** del AI DevOS. No es una descripción de rol, sino una especificación técnica de ejecución determinista.

### Arquitectura de Módulos (24 Motores Nucleares)

| Módulo | Tipo | Responsabilidad Técnica |
| :--- | :---: | :--- |
| `instructions.md` | Core | Protocolo de arranque y bucle de pensamiento central. |
| `decision-engine.md` | Logic | Algoritmo de ruteo 5D (Confianza, Carga, Riesgo). |
| `planning-engine.md` | Execution | Descomposición HTN y gestión de Ruta Crítica. |
| `task-decomposition-engine.md` | Logic | Atomización de requisitos en tareas ejecutables. |
| `risk-analysis-engine.md` | Security | Evaluación de impacto y vectores de ataque. |
| `memory-strategy.md` | Data | Jerarquía L1-L5 y reglas de persistencia. |
| `memory-retrieval-engine.md` | Data | RAG operacional y búsqueda semántica ponderada. |
| `context-management.md` | Optimization | Poda dinámica de ventana de tokens. |
| `context-priority-engine.md` | Logic | Calificación de relevancia de archivos in-context. |
| `mcp-routing.md` | Tools | Gobernanza de herramientas y seguridad de ejecución. |
| `tool-selection-engine.md` | Logic | Racional de selección de herramientas por coste/riesgo. |
| `workflow-rules.md` | Flow | Máquina de estados finitos del sistema de agentes. |
| `workflow-selection-engine.md` | Logic | Selección de topología de equipo (Secuencial vs Paralela). |
| `quality-gates.md` | Quality | Barreras de validación y auto-corrección. |
| `agent-scoring-engine.md` | Meta | Cálculo de fiabilidad y reputación de agentes. |
| `recovery-protocol.md` | Resilience | Estrategias de autocuración y fallback. |
| `failure-classification-engine.md` | Analytics | Taxonomía de errores y diagnóstico preventivo. |
| `escalation-policy.md` | Human | Reglas de transferencia de autoridad al usuario. |
| `conflict-resolution-engine.md` | Meta | Arbitraje entre decisiones de agentes competitivos. |
| `handover-rules.md` | Protocol | Contratos de transferencia de estado (State Transfer). |
| `output-contracts.md` | Schema | Definición de interfaces de salida deterministas. |
| `capability-matrix.md` | Manifest | Inventario de capacidades y límites operativos. |
| `prompt-engine.md` | Generation | Metaprompting y refinamiento de instrucciones. |

### Boot Sequence (Runtime)
1. **POST (Power-On Self-Test):** Verifica integridad de `standards/constitution.md`.
2. **Registry Init:** Carga el catálogo de agentes y sus Health Checks.
3. **Memory Sync:** Recupera el `State` de la última sesión.
4. **Heartbeat:** Emite señal de `READY` en la consola.
