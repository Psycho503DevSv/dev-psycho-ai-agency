# 🧠 PsychoSv_503 — AI DevOS

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/Psycho503DevSv/dev-psycho-ai-agency?style=for-the-badge&logo=github)](https://github.com/Psycho503DevSv/dev-psycho-ai-agency/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Psycho503DevSv/dev-psycho-ai-agency?style=for-the-badge&logo=github)](https://github.com/Psycho503DevSv/dev-psycho-ai-agency/network/members)
[![Last Commit](https://img.shields.io/github/last-commit/Psycho503DevSv/dev-psycho-ai-agency?style=for-the-badge)](https://github.com/Psycho503DevSv/dev-psycho-ai-agency/commits/main)

> **Un Sistema Operativo de Desarrollo de Software Multi-Agente autónomo, vergas y premium.**
> Orquesta un equipo de especialistas virtuales que diseñan, planifican, auditan y previsualizan proyectos de software reales mediante flujos automatizados utilizando la API de NVIDIA NIM, OpenAI y Anthropic.

---

## 🤔 ¿Qué es esto?

Imagínate una empresa de desarrollo de software de alto rendimiento donde **cada empleado es un agente de Inteligencia Artificial especializado**. Hay un CEO que dirige y orquesta, un Product Manager que define y traduce tus ideas a especificaciones técnicas, un Frontend que diseña interfaces interactivas, un Backend que construye APIs robustas, un QA que valida la funcionalidad de cada componente, y un Security Engineer que audita el código buscando vulnerabilidades antes de cada entrega.

### 🔄 Modelo de Trabajo Híbrido (Agente + IDE)
Es fundamental entender que **PsychoSv_503 AI DevOS** no está diseñado para que el agente escriba todo el código de forma aislada.
* **El Agente (DevOS)** actúa como el **Orquestador, Quality Gate y Auto-Trainer**: Define la arquitectura, crea especificaciones, audita vulnerabilidades, valida la sintaxis y cobertura del código, y usa las llaves de API para autoentrenarse analizando logs y escribiendo lecciones aprendidas en `memory/lessons_learned.md`.
* **Las Herramientas e IDEs de IA (OpenCode, Antigravity, Claude o Gemini CLI)** se encargan de la **escritura real del código** y maquetación visual premium a partir de las directrices y validaciones del agente.

Esta separación de responsabilidades garantiza la mayor calidad de código posible, elimina preguntas repetitivas innecesarias del agente y optimiza el consumo de tokens en entornos de producción multi-PC. El equipo de DevOS lee y escribe archivos, ejecuta comandos de consola, audita dependencias, y renderiza visualizaciones automáticas de los proyectos en desarrollo mediante el protocolo **MCP (Model Context Protocol)** y un orquestador persistente.

---

## 🚀 Características Principales

* **Bucle Real de Agentes (Real Agent Loop):** Ejecución de inferencia dinámica usando llamadas directas a APIs HTTP. Los agentes razonan, deciden y llaman herramientas locales en bucles interactivos de hasta 5 turnos. Prioridad nativa para la API de **NVIDIA NIM** (`meta/llama-3.1-8b-instruct`) con fallbacks configurables a **OpenAI**, **Anthropic**, **Gemini** y **Groq**.
* **Rotación Inteligente de Claves (Multi-Key):** Soporte para pools de múltiples API Keys separadas por comas para **Gemini** y **Groq**. El sistema implementa:
  * *Rotación por cuota:* Cambia de clave automáticamente al recibir errores `429 Too Many Requests` o fallos de timeout.
  * *Rotación diaria:* Cicla entre el pool de claves cada 24 horas para balancear el consumo de tokens de forma equitativa.
* **Tipos de Proyecto Nativos:** Soporte y flujo diferenciado para 5 categorías de desarrollo mediante un registro unificado (`registry/project-types-registry.json`):
  * 🌐 `web-estatica`: Prototipos visuales y landing pages en HTML/CSS/JS puro.
  * ⚛️ `web-framework`: Aplicaciones modernas usando React, Vue o Vite (con detección inteligente de `nextjs-monorepo`).
  * 📱 `android-apk`: Compilación directa con Gradle y despliegue físico en emuladores/dispositivos mediante ADB.
  * 🧩 `chrome-extension`: Extensiones de Chrome listas para carga en modo desarrollador.
  * 🎭 `kinetic-typography`: Animaciones de tipografía cinética interactivas (GSAP, Three.js).
* **Previsualización Nativa Automatizada (`preview_project`):** Herramienta MCP capaz de levantar servidores HTTP locales, correr scripts de desarrollo (`npm run dev`), instalar y reemplazar APKs sin duplicados (`adb install -r` con reemplazo de versión), y lanzar Chrome con extensiones cargadas automáticamente.
* **Limpieza Segura del Sandbox (`clean_project_dir`):** Nueva herramienta nativa que permite limpiar subcarpetas específicas dentro del proyecto activo de forma segura, respetando el sandbox y evitando bloqueos de seguridad al recrear scaffolds (por ejemplo, al ejecutar `create-next-app` o `npm init`).
* **Entrevista de Diseño Interactiva (`ask_user`):** Los agentes pausan su ejecución para preguntarte detalles estéticos (colores, tipografías, fondos degradados, animaciones, tipo de proyecto) antes de escribir una sola línea de código.
* **Quality Gate y Validación de Compilación Real:** Validador automático que ejecuta análisis sintácticos y comprueba la presencia de archivos obligatorios (`README.md`, `requirements.txt`). Además, en proyectos de Node.js/web-framework, el gate realiza un `npm install` y un build real de compilación (`npm run build`) para garantizar que la entrega no tenga errores de tipado o dependencias.
* **Sistema Auto-Learner:** Cuando un flujo termina, el sistema extrae automáticamente los errores del Quality Gate y los documenta en `memory/lessons_learned.md` para evitar regresiones y asegurar que el equipo no vuelva a cometer el mismo fallo.

---

## 📦 Instalación paso a paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Psycho503DevSv/dev-psycho-ai-agency.git
cd dev-psycho-ai-agency
```

### 2. Crear y Activar el Entorno Virtual
```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# Linux / Mac
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (`.env`)
Crea un archivo `.env` en la raíz del proyecto. El motor soporta múltiples proveedores y rotación inteligente de claves. Configura tus tokens según tus necesidades:

```env
# ── Gemini (Google AI Studio — Soporta multi-key separadas por comas)
# Consíguelas gratis en: https://aistudio.google.com/apikey
GEMINI_API_KEY=AIzaSyKey1,AIzaSyKey2,AIzaSyKey3

# ── Groq (Velocidad muy alta — Soporta multi-key separadas por comas)
# Consíguelas gratis en: https://console.groq.com/keys
GROQ_API_KEY=gsk_key1,gsk_key2

# ── NVIDIA NIM (Auto-Aprendizaje / Memoria)
NVIDIA_API_KEY=nvapi-tu_clave_aquí

# ── Proveedores de pago / Otras APIs
OPENAI_API_KEY=sk-proj-tu_clave_aquí
ANTHROPIC_API_KEY=sk-ant-tu_clave_aquí

# ── Integraciones de Despliegue del Usuario (Opcionales)
# Registra tus propios tokens de desarrollo para que los agentes puedan realizar 
# despliegues en Vercel, interactuar con bases de datos Supabase o hacer push a GitHub.
VERCEL_TOKEN=tkn_tu_token_de_vercel
SUPABASE_URL=https://tu_proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
SUPABASE_DB_URL=postgresql://postgres:password@db.tu_proyecto.supabase.co:5432/postgres
GITHUB_TOKEN=ghp_tu_token_de_github

# ── Configuración de Grafo de Memoria
USE_GRAPHITI=false
```
*Si no configuras ninguna clave de API, el sistema correrá los pasos en **Modo Simulación** de manera gratuita sin consumir créditos ni tokens.*

---

## 💻 Cómo Usarlo

Inicia la orquestación indicando el workflow que deseas ejecutar y el nombre del proyecto en desarrollo:

```bash
python -m runtime.workflow_runner [workflow_id] [nombre_proyecto]
```

### Ejemplos Rápidos de Uso:

1. **Descubrimiento y Entrevista Inicial:**
   *Entrevista al usuario sobre la visión de su software y genera los requisitos iniciales.*
   ```bash
   python -m runtime.workflow_runner wf-discovery mi-proyecto-web
   ```
2. **Construcción Completa:**
   *Planifica, diseña, codifica y valida un proyecto completo desde cero.*
   ```bash
   python -m runtime.workflow_runner wf-build-project mi-dashboard-react
   ```
3. **Revisión y Auditoría:**
   *Ejecuta pruebas funcionales y escaneo de vulnerabilidades de seguridad en el código existente.*
   ```bash
   python -m runtime.workflow_runner wf-review mi-app-android
   ```
4. **Mantenimiento y Corrección:**
   *Localiza y soluciona bugs aplicando el bucle cerrado del QA y el Desarrollador.*
   ```bash
   python -m runtime.workflow_runner wf-maintenance mi-proyecto-web
   ```

---

## 🏗️ Arquitectura del Sistema

El workspace se organiza de forma modular para garantizar la escalabilidad de agentes y flujos de trabajo:

```
PsychoSv_503/
│
├── 🤖 agents/              → Los "empleados" — instrucciones operativas y prompts de cada agente
│   ├── psycho-ceo/         → El jefe central: entrevista al usuario, valida pasos y coordina la entrega
│   ├── product-manager/    → Gestiona los requisitos y los traduce a especificaciones técnicas
│   ├── frontend/           → Desarrollo de interfaces, maquetación visual y animaciones
│   ├── backend/            → Creación de APIs, lógica de base de datos y scripts de servidor
│   ├── devops/             → Scripting de automatización, empaquetado, ADB y despliegue
│   ├── qa/                 → Planificación de pruebas funcionales y unitarias
│   ├── security/           → Auditoría de ciberseguridad, dependencias y inyecciones
│   ├── ai-architect/       → Diseña integraciones de inteligencia artificial y modelos
│   ├── mcp-architect/      → Diseña la arquitectura e integración de herramientas MCP
│   ├── rag-architect/      → Estructura la memoria semántica y bases de datos vectoriales
│   ├── context-engineer/   → Optimiza el uso de tokens y la compresión de contexto
│   ├── agent-evaluator/    → Validador técnico de la salida de otros agentes antes de finalizar
│   └── orchestrator/       → Subcoordinador para tareas y micro-servicios complejos
│
├── ⚙️ config/              → Configuración central del sistema
│   └── settings.py         → Carga de variables de entorno, llaves API y paths del workspace
│
├── 📚 docs/                → Documentación técnica e informes
│
├── 🧠 memory/              → La memoria del sistema (Híbrida y persistente)
│   ├── active_context.md   → ¿En qué está trabajando el sistema ahora mismo?
│   ├── architecture.md     → Decisiones tecnológicas y de diseño tomadas
│   ├── decisions.md        → Historial y log de decisiones críticas
│   ├── requirements.md     → Requisitos y alcance del proyecto activo
│   ├── tasks.md            → Lista de tareas pendientes y completadas (TODO)
│   ├── lessons_learned.md  → Lecciones aprendidas a partir del validador de errores
│   ├── project_state.json  → Estado completo del proyecto en formato estructurado JSON
│   └── sessions/           → Logs JSON detallados de la ejecución de cada sesión
│
├── 🔌 mcps/                → Servidores MCP (Model Context Protocol)
│   ├── core/               → Servidores de herramientas esenciales (filesystem, git, browser)
│   ├── community/          → Herramientas extendidas de la comunidad
│   └── custom/             → Herramientas personalizadas para la agencia
│
├── 📁 projects/            → Directorio de salida para los proyectos creados por los agentes
│
├── 📋 registry/            → Registros centrales del sistema
│   ├── agent-registry.json     → Lista de agentes habilitados y sus metadatos
│   ├── project-types-registry.json → Registro nativo de los 5 tipos de proyectos soportados
│   ├── mcp-registry.json       → Configuración de servidores MCP y permisos de acceso
│   └── workflow-registry.json  → Definición detallada de los workflows
│
├── ⚡ runtime/             → El motor de ejecución (Runtime Core)
│   ├── agent_loader.py     → Carga agentes e inyecta memoria en base al rol (filtra tokens)
│   ├── memory_engine.py    → Persistencia de memoria (soporte local JSON y Graphiti Neo4j)
│   ├── graphiti_bridge.py  → Conector opcional hacia bases de datos de grafos semánticos
│   ├── quality_gate.py     → Validador automático de código antes de la entrega
│   └── workflow_runner.py  → Controlador principal del bucle interactivo de la agencia
│
└── 📐 standards/           → Leyes y guías de desarrollo aplicadas a los agentes
    ├── constitution.md         → La constitución y ley suprema de la agencia
    ├── coding-standards.md     → Estándares de calidad de código
    ├── security-standards.md   → Estándares de ciberseguridad
    ├── documentation-standards.md → Estándares de documentación de entregas
    ├── communication-standards.md → Normas de comunicación interna entre agentes
    └── mcp-governance.md       → Gobernanza de permisos de herramientas locales
```

---

## 🤖 Agentes Principales y Jerarquía

El equipo se divide en niveles de jerarquía y responsabilidad para optimizar el consumo de tokens y asegurar que no haya colisiones en la toma de decisiones:

| Nivel | Agente | Rol en la Agencia | Acceso a Memoria |
| :--- | :--- | :--- | :--- |
| 👑 **Nivel 1** | `psycho-ceo` | Orquestador supremo, realiza la entrevista inicial al usuario, gestiona el alcance y decide la aprobación de entregas. | Total (Lectura/Escritura) |
| 🎯 **Nivel 2** | `agent-evaluator` | Validador de calidad. Revisa la salida técnica de los especialistas y da visto bueno. | Lectura/Escritura |
| 🎯 **Nivel 2** | `product-manager` | Diseñador del alcance técnico. Traduce los requisitos a listas de tareas. | Lectura/Escritura |
| 💻 **Nivel 3** | `frontend` | Diseña interfaces interactivas, animaciones kinetic y layouts responsivos. | Lectura/Escritura |
| 🔧 **Nivel 3** | `backend` | Construye APIs, integra bases de datos y maneja endpoints y configuraciones. | Lectura/Escritura |
| 🚀 **Nivel 3** | `devops` | Empaqueta el código, compila ejecutables/APKs y maneja scripts de inicio. | Lectura/Escritura |
| 🔒 **Nivel 3** | `security` | Audita dependencias (`pip audit` / `npm audit`), y detecta riesgos de inyección. | Lectura/Escritura |

---

## 🔄 Flujos de Trabajo (Workflows)

Los workflows coordinan a los agentes secuencialmente para cumplir objetivos globales:

| ID del Workflow | Nombre | Propósito | Secuencia de Agentes |
| :--- | :--- | :--- | :--- |
| `wf-discovery` | Descubrimiento | Capturar la visión del cliente mediante la entrevista y crear requisitos iniciales. | `psycho-ceo` → `product-manager` |
| `wf-planning` | Planificación | Diseñar la estructura del software, base de datos y dependencias. | `psycho-ceo` → `ai-architect` → `product-manager` |
| `wf-implementation`| Implementación | Desarrollar código y previsualizar de forma autónoma con el usuario. | `psycho-ceo` → `frontend` → `backend` → `agent-evaluator` |
| `wf-review` | Revisión | Auditoría funcional, de código y de seguridad antes del despliegue. | `psycho-ceo` → `qa` → `security` → `agent-evaluator` |
| `wf-maintenance` | Mantenimiento | Corrección de bugs e iteración incremental de la base de código. | `psycho-ceo` → `backend` → `qa` → `devops` |
| `wf-build-project` | Construcción Completa | Desarrollo completo de extremo a extremo, desde la entrevista al código aprobado. | `psycho-ceo` → `product-manager` → `ai-architect` → `frontend` → `backend` → `agent-evaluator` |

---

## 🧠 Sistema de Memoria Híbrida y Persistente

Para evitar el olvido cognitivo común en sistemas multi-agente, PsychoSv_503 implementa una arquitectura de memoria estructurada y compartida:

1. **Lectura Contextualizada (Token Saving):** Cuando `agent_loader.py` prepara a un agente, no inyecta todo el historial del proyecto. Lee e inyecta selectivamente solo las partes de `memory/` relevantes para su rol (ej. el backend no lee estilos CSS detallados, solo los esquemas de bases de datos).
2. **Archivos de Memoria Compartida:**
   * `active_context.md`: El estado actual del sprint de desarrollo.
   * `requirements.md`: La especificación formal y el alcance del producto.
   * `tasks.md`: El tablero de control (TODO list) que coordina el progreso.
   * `lessons_learned.md`: Los errores de sintaxis y lógica detectados en el pasado para evitar que se repitan en futuras iteraciones.
3. **Persistencia Local y Grafo:**
   * **Modo Local (Activo por Defecto):** Gratuito y 100% offline. Guarda todo en archivos estructurados JSON dentro de `memory/sessions/`.
   * **Modo Graphiti (Opcional):** Si se configura `USE_GRAPHITI=true` en el `.env`, el sistema sincroniza con una base de datos Neo4j para mapear entidades y relaciones complejas del software desarrollado.

---

## ⚡ El Motor de Ejecución (Runtime)

El core del sistema operativo de desarrollo corre a través de 4 componentes críticos en la carpeta `runtime/`:

### `agent_loader.py`
Responsable de instanciar cada agente técnico inyectando en su contexto los prompts del sistema, estándares del repositorio y la información filtrada de memoria.

### `memory_engine.py`
Gestor del estado y persistencia de la memoria de las sesiones. Encargado de serializar los entregables intermedios de los agentes.

### `mcp_executor.py`
El despachador de herramientas. Actúa como el intérprete entre los comandos JSON producidos por el LLM y el sistema operativo del usuario. Implementa:
* Operaciones de archivos con guardrails de seguridad.
* Ejecución de terminal controlada con timeout síncrono.
* Lanzamiento de previsualizaciones nativas (`preview_project`).

### `workflow_runner.py`
El motor de orquestación. Carga los workflows del registro, itera el bucle real del LLM, despacha herramientas locales al executor, y maneja transiciones de estado (`IDLE` ➡️ `RUNNING` ➡️ `SUCCESS` / `FAILED`).

---

## 📐 La Constitución y Reglas de Oro

El archivo `standards/constitution.md` rige el comportamiento de todos los agentes. Si un agente rompe estas reglas, el `agent-evaluator` rechazará su propuesta de código:

### Reglas de Oro Obligatorias:
1. **No Immediate Coding 🧠:** Ningún agente escribe código directamente. Primero debe analizar los requisitos (`requirements.md`), revisar las decisiones de diseño y definir los pasos a seguir.
2. **Document Decisions 📝:** Cualquier elección tecnológica, puerto de previsualización o arquitectura debe ser registrada en `memory/decisions.md`.
3. **Document Changes 🔄:** Todo cambio en la funcionalidad debe ser documentado en los archivos correspondientes dentro de `__docs__/`.
4. **Maintainability First 🛠️:** Código limpio, estructurado y modular sobre implementaciones rápidas o acopladas.

### Jerarquía de Autoridad
1. 📜 **Constitución**
2. 🔒 **Estándares de Seguridad**
3. 🏗️ **Estándares de Arquitectura**
4. 📋 **Requisitos del Proyecto**
5. 🤖 **Instrucciones del Agente**

---

## 🛠️ Tecnologías Usadas (Tech Stack)

* **Core Runtime:** Python 3.10+
* **LLM & Inferencia:** NVIDIA NIM (Llama 3.1 8B Instruct - Prioritario) / OpenAI (GPT-4o mini - Fallback)
* **Entornos de Previsualización:**
  * Servidores Web locales integrados (Python HTTP Server)
  * Node.js & Vite (para compilaciones React/Vue/Framework)
  * Android Debug Bridge (ADB) + Gradle (para Apps Android en emuladores o dispositivos físicos)
  * Google Chrome CLI (para extensiones de Chrome locales en tiempo de desarrollo)
* **Pruebas de Software:** Pytest & Unittest Mocks

---

## 🧪 Compatibilidad con IDEs y Modelos

Este sistema operativo multi-agente está diseñado para integrarse con herramientas de desarrollo de software modernas:

* **IDEs Habilitados:** Antigravity IDE, VS Code, Cursor, OpenCode.
* **Modelos Compatibles:** Claude (Anthropic), Gemini (Google), Llama (Meta/NVIDIA), Grok (xAI).

---

## 🗺️ Roadmap / Próximos Pasos

* [ ] Implementación de RAG semántico local para bases de datos vectoriales en disco.
* [ ] Integración nativa de Playwright para generación y ejecución de pruebas end-to-end automáticas por el agente QA.
* [ ] Contenedores Docker pre-configurados para el empaquetado seguro de entornos de desarrollo.
* [x] Dashboard web visual interactivo para monitorear el flujo de mensajes de los agentes en tiempo real (Military Command Center).

---

## 📄 Licencia

Este proyecto está liberado bajo la Licencia **MIT**. Puedes usarlo, modificarlo y distribuirlo libremente en proyectos comerciales o personales.

---

### Made with ❤️ by [Psycho503](https://github.com/Psycho503DevSv)
