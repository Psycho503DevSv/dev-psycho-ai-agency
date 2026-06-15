# 🧠 PsychoSv_503 — AI DevOS

> **Sistema Operativo de Desarrollo con Inteligencia Artificial**
> Un ecosistema de agentes especializados que trabajan juntos como una agencia de software virtual. Diseña, planifica, construye y valida proyectos completos usando múltiples LLMs coordinados.

---

## 🤔 ¿Qué es esto?

Imagínate una empresa de desarrollo de software donde **cada empleado es una IA especializada**. Hay un CEO que dirige, un Product Manager que planifica, un Frontend que diseña interfaces, un Backend que construye APIs, un QA que prueba todo y un Security que busca vulnerabilidades.

**PsychoSv_503** es exactamente eso: un sistema donde tú eres el dueño de la empresa y los agentes de IA son tu equipo completo. Solo les dices qué quieres construir y ellos se organizan solos para hacerlo.

---

## 🏗️ Arquitectura del Sistema

```
PsychoSv_503/
│
├── 🤖 agents/              → Los "empleados" — instrucciones de cada agente
│   ├── psycho-ceo/         → El jefe: orquesta y dirige a todos
│   ├── product-manager/    → Traduce tus ideas a requisitos técnicos
│   ├── ai-architect/       → Diseña la arquitectura de IA del sistema
│   ├── frontend/           → Construye interfaces web (HTML, CSS, React)
│   ├── backend/            → Construye APIs, bases de datos y servidores
│   ├── devops/             → Despliega y mantiene la infraestructura
│   ├── qa/                 → Prueba y valida la calidad del código
│   ├── security/           → Detecta y corrige vulnerabilidades
│   ├── mcp-architect/      → Diseña la integración con herramientas (MCP)
│   ├── rag-architect/      → Diseña sistemas de búsqueda y recuperación
│   ├── context-engineer/   → Optimiza el uso de tokens y contexto
│   ├── agent-evaluator/    → Evalúa el output de todos los agentes
│   └── orchestrator/       → Subcoordinador de flujos complejos
│
├── ⚙️ config/              → Configuración central del sistema
│   └── settings.py         → Variables de entorno, rutas y flags
│
├── 📚 docs/                → Documentación técnica y reportes
│
├── 🧠 memory/              → La "memoria" del sistema
│   ├── active_context.md   → ¿En qué está trabajando el sistema ahora?
│   ├── architecture.md     → Decisiones de arquitectura tomadas
│   ├── decisions.md        → Log de decisiones importantes
│   ├── requirements.md     → Requisitos del proyecto activo
│   ├── tasks.md            → Tareas pendientes y en progreso
│   ├── lessons_learned.md  → Errores del pasado y cómo evitarlos
│   ├── project_state.json  → Estado actual del proyecto en formato JSON
│   ├── sessions/           → Logs de cada sesión de trabajo (JSON)
│   └── patterns/           → Patrones reutilizables aprendidos
│
├── 🔌 mcps/                → Servidores MCP (herramientas externas)
│   ├── core/               → MCPs esenciales (filesystem, git, browser)
│   ├── community/          → MCPs de la comunidad
│   └── custom/             → MCPs creados a medida
│
├── 📁 projects/            → Directorio de trabajo para cada proyecto
│
├── 📋 registry/            → Registros centrales del sistema
│   ├── agent-registry.json     → Lista y configuración de todos los agentes
│   ├── workflow-registry.json  → Definición de los flujos de trabajo
│   ├── mcp-registry.json       → Herramientas habilitadas y permisos
│   └── tool-registry.json      → Herramientas de Python disponibles
│
├── ⚡ runtime/             → El motor de ejecución del sistema
│   ├── agent_loader.py     → Carga agentes e inyecta memoria en su contexto
│   ├── memory_engine.py    → Motor de memoria (local JSON + Graphiti opcional)
│   ├── graphiti_bridge.py  → Puente opcional hacia Neo4j / Graphiti
│   ├── quality_gate.py     → Validador automático de código generado
│   └── workflow_runner.py  → Orquestador de flujos multi-agente
│
├── 📐 standards/           → Las reglas que todos los agentes deben seguir
│   ├── constitution.md         → La ley suprema del sistema
│   ├── coding-standards.md     → Estándares de código
│   ├── security-standards.md   → Reglas de seguridad
│   ├── documentation-standards.md → Cómo documentar
│   ├── communication-standards.md → Cómo se comunican los agentes
│   └── mcp-governance.md       → Qué herramientas puede usar cada agente
│
├── 📦 templates/           → Plantillas base para crear nuevos componentes
│   ├── agent-template/     → Base para crear un nuevo agente
│   ├── mcp-template/       → Base para integrar un nuevo MCP
│   └── workflow-template/  → Base para definir un nuevo workflow
│
├── 🛠️ tools/               → Scripts de utilidad para el sistema
│   ├── health-check.py         → Verifica que el sistema esté sano
│   ├── mcp_diagnostics.py      → Diagnóstico de herramientas MCP
│   ├── mcp_installer.py        → Instala MCPs nuevos
│   └── registry_schema_validator.py → Valida los registros JSON
│
└── 🔄 workflows/           → Definiciones de los flujos de trabajo
    ├── project-discovery.md    → Flujo: descubrir y entender requisitos
    ├── project-planning.md     → Flujo: planificar la arquitectura
    ├── project-implementation.md → Flujo: construir el proyecto
    ├── project-review.md       → Flujo: revisar y validar
    ├── project-maintenance.md  → Flujo: mantener y corregir bugs
    └── project-release.md      → Flujo: lanzar a producción
```

---

## 🤖 Los Agentes y sus Roles

| Nivel | Agente | Rol | Acceso a Memoria |
|-------|--------|-----|-----------------|
| 👑 1 | `psycho-ceo` | CEO y Orquestador Central | Total |
| 🎯 2 | `agent-evaluator` | Control de Calidad | Lectura/Escritura |
| 🎯 2 | `product-manager` | Gestión de Producto | Lectura/Escritura |
| 💻 3 | `frontend` | Ingeniería Frontend | Lectura/Escritura |
| 🔧 3 | `backend` | Ingeniería Backend | Lectura/Escritura |
| 🚀 3 | `devops` | DevOps e Infraestructura | Lectura/Escritura |
| 🧪 3 | `qa` | Control de Calidad | Lectura/Escritura |
| 🔒 3 | `security` | Seguridad | Lectura/Escritura |
| 🧱 3 | `ai-architect` | Arquitectura de IA | Lectura/Escritura |
| 🔌 3 | `mcp-architect` | Arquitectura MCP | Lectura/Escritura |
| 🔍 3 | `rag-architect` | Arquitectura RAG | Lectura/Escritura |
| 🎛️ 3 | `context-engineer` | Ingeniería de Contexto | Lectura/Escritura |

---

## 🔄 Flujos de Trabajo (Workflows)

Un **workflow** es una secuencia de agentes que trabajan en orden para completar una tarea completa. El sistema tiene 6 flujos predefinidos:

| ID | Nombre | ¿Cuándo se usa? | Agentes involucrados |
|----|--------|-----------------|---------------------|
| `wf-discovery` | Project Discovery | Al inicio, cuando tienes una idea | CEO → Product Manager |
| `wf-planning` | Project Planning | Cuando los requisitos están listos | CEO → AI Architect → PM |
| `wf-implementation` | Project Implementation | Cuando el plan está aprobado | CEO → Frontend → Backend → Evaluator |
| `wf-review` | Project Review | Al terminar una tarea | CEO → QA → Security → Evaluator |
| `wf-maintenance` | Project Maintenance | Cuando hay un bug | CEO → Backend → QA → DevOps |
| `wf-build-project` | Build Full Project | Para construir desde cero | CEO → PM → Architect → Frontend → Backend → Evaluator |

---

## 🧠 Sistema de Memoria

El sistema tiene memoria persistente para no olvidar nada entre sesiones.

### ¿Cómo funciona?

1. Cuando un agente trabaja, **guarda lo que hizo** en `memory/sessions/` como archivos JSON.
2. Cuando un agente va a trabajar, el **`agent_loader.py` lee solo los archivos de memoria relevantes** para su rol (no toda la memoria, para no desperdiciar tokens).
3. Los **patrones aprendidos** se promueven a `memory/patterns/` para que todos los agentes los usen en el futuro.

### Archivos de Memoria Compartida

| Archivo | ¿Qué contiene? |
|---------|----------------|
| `active_context.md` | Lo que está haciendo el sistema ahora mismo |
| `architecture.md` | Decisiones de arquitectura del proyecto actual |
| `decisions.md` | Log de decisiones importantes tomadas |
| `requirements.md` | Requisitos del proyecto activo |
| `tasks.md` | Lista de tareas pendientes y completadas |
| `lessons_learned.md` | Errores del pasado para no repetirlos |
| `project_state.json` | Estado completo del proyecto en JSON |

### Modos de Memoria

#### 🗂️ Modo Local — **ACTIVO POR DEFECTO, no necesitas configurar nada**
Guarda todo como archivos JSON en tu disco duro. **100% privado, gratuito y sin internet.**
No necesitas crear ningún archivo `.env`. El sistema arranca en este modo automáticamente.

#### 🕸️ Modo Graphiti / Neo4j — ⚠️ OPCIONAL y AVANZADO (no recomendado para empezar)
> ⚠️ **Este modo está DESACTIVADO por defecto.** Solo configúralo si sabes lo que haces. Requiere instalar Neo4j y tener una API Key de OpenAI.

Si en el futuro quisieras activarlo, creas un archivo `.env` en la raíz **con este valor en `true`**:
```ini
# SOLO si quieres activar el modo grafo (no es necesario)
USE_GRAPHITI=true
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu_contraseña
OPENAI_API_KEY=tu_clave
```

---

## ⚡ El Motor de Ejecución (Runtime)

El corazón del sistema son 4 archivos Python en la carpeta `runtime/`:

### `agent_loader.py`
Carga a los agentes desde el registro y construye su contexto de trabajo. Antes de ejecutar un agente, **inyecta automáticamente en su prompt solo la memoria relevante** para su rol, reduciendo el consumo de tokens al mínimo.

### `memory_engine.py`
Motor de persistencia de memoria. Soporta dos modos:
- **Local:** Guarda y recupera datos en archivos JSON en `memory/sessions/`.
- **Graphiti:** Si está habilitado, también sincroniza con una base de datos de grafos.

### `quality_gate.py`
Validador automático que corre antes de entregar cualquier código generado. Verifica:
- ✅ Sintaxis correcta de todos los archivos `.py`
- ✅ Presencia de archivos obligatorios (`README.md`, `requirements.txt`)

### `workflow_runner.py`
El orquestador de flujos. Recibe un `workflow_id` y un nombre de proyecto, carga los agentes en orden, ejecuta cada paso y registra el resultado en memoria.

---

## 📐 La Constitución del Sistema

El archivo `standards/constitution.md` es la **ley suprema** que todos los agentes deben obedecer. Define:

1. **Prioridad del Usuario:** Todo desarrollo aporta valor real.
2. **Integridad del Sistema:** Ninguna acción compromete la estabilidad.
3. **Persistencia del Conocimiento:** Las decisiones se documentan siempre.
4. **Claridad Lingüística:** El español es el idioma oficial del sistema.

### Jerarquía de Autoridad (de mayor a menor)
1. 📜 Constitución
2. 🔒 Estándares de Seguridad
3. 🏗️ Estándares de Arquitectura
4. 📋 Requisitos del Proyecto
5. 🤖 Instrucciones del Agente

---

## 🔌 Herramientas (MCPs)

Los **Model Context Protocols (MCPs)** son las herramientas que los agentes pueden usar para interactuar con el mundo real:

| MCP | Tipo | ¿Para qué sirve? |
|-----|------|-----------------|
| `filesystem` | Core | Leer y escribir archivos en disco |
| `git` | Core | Hacer commits y pushes a GitHub |
| `browser` | Core | Navegar y extraer información de páginas web |
| `memory-layer` | Custom | Leer y escribir en el sistema de memoria |
| `docker` | Infrastructure | Gestionar contenedores Docker |
| `fetch` | Web | Hacer peticiones HTTP / Web scraping |
| `playwright` | Browser | Automatización de navegadores para testing |

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/Psycho503DevSv/dev-psycho-ai-agency.git
cd dev-psycho-ai-agency
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar Claves de API (.env)

Para que el bucle de agentes funcione de manera autónoma y real (utilizando modelos de lenguaje reales), debes configurar un archivo `.env` en la raíz del proyecto. El sistema soporta dos modos de ejecución:

* **Modo Real (NVIDIA NIM o OpenAI):** Si configuras una clave en el archivo `.env`, los agentes realizarán llamadas de razonamiento y uso de herramientas reales en cada paso.
* **Modo Simulación:** Si no configuras ninguna clave de API, el sistema correrá los pasos en modo simulación de manera gratuita sin consumir créditos ni tokens.

Crea un archivo `.env` con la siguiente estructura:
```env
# Clave del API gratuita de NVIDIA NIM (Recomendada y prioritaria si se define)
# Consíguela gratis en: https://build.nvidia.com/
NVIDIA_API_KEY=nvapi-tu_clave_aquí

# Clave de OpenAI (Opcional, de compatibilidad)
OPENAI_API_KEY=
```

### 4. Ejecutar un workflow
```bash
python -m runtime.workflow_runner [workflow_id] [nombre_proyecto]
```

**Ejemplos:**
```bash
# Descubrir requisitos de un nuevo proyecto
python -m runtime.workflow_runner wf-discovery mi-app-web

# Construir un proyecto completo desde cero
python -m runtime.workflow_runner wf-build-project mi-saas-app

# Revisar y validar el código de un proyecto
python -m runtime.workflow_runner wf-review mi-app-web
```

### 4. Verificar la salud del sistema
```bash
python tools/health-check.py
```

### 5. Correr las pruebas unitarias
```bash
# Ejecutar todas las pruebas con pytest
pytest
```

---

## 🛡️ Reglas de Oro (Cómo trabajan los agentes)

### Regla #1 — No Immediate Coding 🧠
Ningún agente escribe código inmediatamente. El flujo siempre es:
1. Análisis de requisitos
2. Revisión de documentación existente
3. Validación de arquitectura
4. Detección de riesgos
5. Planificación de implementación
6. Código y ejecución

### Regla #2 — Document Decisions 📝
Toda decisión arquitectónica o de diseño crítica debe quedar documentada en `memory/decisions.md`.

### Regla #3 — Document Changes 🔄
Cada modificación al código debe actualizar la documentación correspondiente.

### Regla #4 — Maintainability First 🛠️
Cada funcionalidad se implementa pensando en la mantenibilidad futura. Código limpio por encima de código rápido.

---

## 🧪 Compatibilidad con IDEs y LLMs

Este sistema está diseñado para funcionar con cualquier entorno de desarrollo moderno que soporte agentes IA:

**IDEs compatibles:**
- Antigravity IDE ✅
- VS Code + GitHub Copilot ✅
- OpenCode ✅
- Cursor ✅

**Modelos LLM compatibles:**
- Google Gemini ✅
- Anthropic Claude ✅
- OpenAI GPT ✅
- xAI Grok ✅
- Alibaba Qwen ✅

---

## 📄 Licencia

Este proyecto es de código abierto bajo la **Licencia MIT**.
Puedes usarlo, modificarlo y distribuirlo libremente.

---

*PsychoSv_503 — Construido con 🔥 por [@Psycho503DevSv](https://github.com/Psycho503DevSv)*
