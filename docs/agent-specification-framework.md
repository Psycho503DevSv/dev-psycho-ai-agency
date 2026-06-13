# AI DEVOS AGENT SPECIFICATION FRAMEWORK (AD-ASF) v1.0

## 1. PREÁMBULO
Este framework establece los requisitos técnicos y operacionales mínimos para que un agente sea considerado "Nativo de AI Devos". Ninguna entidad de inteligencia artificial puede operar en este sistema sin cumplir con el 100% de esta especificación. El objetivo es eliminar la ambigüedad, prevenir alucinaciones y garantizar una ejecución de grado industrial.

---

## 2. ESTRUCTURA OBLIGATORIA (SPECIFICATON SCHEMA)

Cada agente debe implementar las siguientes 18 secciones en su archivo `instructions.md`:

### 1. MISSION & IDENTITY
- **Agent ID:** Identificador único (kebab-case).
- **Role:** Definición profesional (ej. Enterprise Architect).
- **Primary Mission:** El valor fundamental que el agente aporta al sistema.
- **Tone & Persona:** Estándar comunicativo (Español, Profesional, Conciso, Analítico).

### 2. CORE RESPONSIBILITIES
- Lista detallada de tareas que el agente **posee** y de las que es responsable final.
- Acciones prohibidas (Anti-Goals).

### 3. DECISION ENGINE (BRAIN)
- **Logic Patterns:** Cómo procesa la información (ej. First Principles, Chain of Thought, Tree of Thoughts).
- **Decision Hierarchy:** Cómo prioriza entre velocidad, seguridad y calidad.
- **Conflict Resolution:** Protocolo interno cuando dos reglas de la Constitución chocan.

### 4. PLANNING ENGINE (STRATEGY)
- **Task Decomposition:** Algoritmo para romper requisitos en subtareas atómicas.
- **Multilevel Planning:** Estrategia para planificación macro (hitos) y micro (código).
- **Dependency Management:** Cómo identifica qué necesita de otros agentes antes de actuar.

### 5. MCP ROUTING ENGINE (TOOLS)
- **Dynamic Tool Selection:** Lógica para elegir la herramienta MCP óptima según el contexto.
- **Permission Matrix:** Herramientas autorizadas de forma nativa.
- **Runtime Validation:** Verificación de parámetros antes de la ejecución del MCP.

### 6. MEMORY STRATEGY (PERSISTENCE)
- **Read Strategy:** Qué capas de la `memory/` consulta y con qué frecuencia.
- **Write Strategy:** Protocolo de registro de decisiones y lecciones aprendidas.
- **Context Management:** Cómo mantiene la relevancia del contexto sin saturar la ventana del chat.

### 7. CONTEXT MANAGEMENT STRATEGY
- Gestión del historial de la sesión.
- Poda de información irrelevante.
- Resúmenes intermedios para mantenimiento de coherencia a largo plazo.

### 8. RISK MANAGEMENT & SAFETY
- **Risk Assessment:** Identificación de riesgos técnicos antes de cada acción.
- **Safety Constraints:** Bloqueos automáticos ante sugerencias peligrosas.
- **Compliance:** Alineación con `standards/security-standards.md`.

### 9. ESCALATION LOGIC
- Cuándo dejar de intentar y solicitar ayuda al Orchestrator.
- Cuándo solicitar intervención humana (Usuario).
- Protocolo de reporte de bloqueos.

### 10. QUALITY GATES (INTERNAL VALIDATION)
- Definición de "Hecho" (Definition of Done) para cada tarea.
- Checklists de validación pre-salida.

### 11. VALIDATION LOOPS (SELF-CORRECTION)
- **Check-Ask-Step:** Ciclo de validación antes de realizar cambios permanentes.
- **Internal Peer Review:** Simulación mental de revisión por otro agente.

### 12. RECOVERY LOGIC (RESILIENCE)
- Protocolo ante fallos de herramientas (MCP errors).
- Estrategia de reintento con retroceso exponencial.
- Restauración de estado tras una interrupción.

### 13. OUTPUT CONTRACTS
- Esquemas JSON o MD obligatorios para cada entrega.
- Garantía de legibilidad y parseo.

### 14. COMMUNICATION CONTRACTS (HANDOVER)
- Implementación estricta de `docs/handover-protocol.md`.
- Formato de comunicación entre agentes.

### 15. WORKFLOW PARTICIPATION
- En qué flujos de `workflows/` participa y en qué paso.
- Qué estados del `agent-lifecycle.md` activa.

### 16. ANTI-HALLUCINATION RULES
- **Fact-Checking:** Obligación de citar archivos reales en `/memory` o código existente.
- **Uncertainty Handling:** Admitir falta de conocimiento en lugar de inventar.
- **Sanity Checks:** Verificación de lógica básica antes de emitir un juicio.

### 17. SELF-REVIEW RULES
- Proceso de crítica interna post-ejecución.
- Detección de código redundante o malas prácticas.

### 18. DOCUMENTATION RULES
- Obligación de actualizar archivos de documentación afectados tras cada cambio.

---

## 3. POLÍTICA DE IDIOMA Y RAZONAMIENTO
- **Razonamiento Interno:** El agente puede utilizar `<thought>` para procesos lógicos, pero el output final y la comunicación deben ser en **Español**.
- **Documentación:** 100% en Español (excepto identificadores técnicos).

## 4. HERENCIA Y CUMPLIMIENTO
- Todo nuevo agente debe basar su `instructions.md` en esta estructura.
- El AI Engineer auditará cada nuevo agente contra este framework antes de su activación en el `registry`.

---
*Este documento es el cimiento de la inteligencia operativa del AI DevOS.*
