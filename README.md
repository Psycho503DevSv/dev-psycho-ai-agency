# 🧠 PsychoSv_503 — AI DevOS

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/Psycho503DevSv/dev-psycho-ai-agency?style=for-the-badge&logo=github)](https://github.com/Psycho503DevSv/dev-psycho-ai-agency/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Psycho503DevSv/dev-psycho-ai-agency?style=for-the-badge&logo=github)](https://github.com/Psycho503DevSv/dev-psycho-ai-agency/network/members)
[![Last Commit](https://img.shields.io/github/last-commit/Psycho503DevSv/dev-psycho-ai-agency?style=for-the-badge)](https://github.com/Psycho503DevSv/dev-psycho-ai-agency/commits/main)

> **Un Sistema Operativo de Desarrollo de Software Multi-Agente autónomo, vergas y premium.**
> Orquesta un equipo de especialistas virtuales que diseñan, planifican, construyen, prueban y previsualizan proyectos de software reales mediante flujos automatizados utilizando la API de NVIDIA NIM y OpenAI.

---

## 🤔 ¿Qué es esto?

**PsychoSv_503 AI DevOS** no es solo una biblioteca de prompts. Es una **agencia de desarrollo de software autónoma y real**. 

Cada rol dentro de una empresa tecnológica tradicional está representado por un agente de inteligencia artificial especializado: desde el CEO que lidera y orquesta, pasando por el Product Manager que analiza los requisitos, hasta ingenieros de Frontend, Backend, QA y Ciberseguridad.

Tú actúas como el dueño del producto. Defines tu idea en la entrevista interactiva inicial y los agentes colaboran en paralelo, escriben código de producción, realizan auditorías de seguridad, y ejecutan herramientas locales gracias al protocolo **MCP (Model Context Protocol)** y un ejecutor local robusto.

---

## 🚀 Características Principales

* **Bucle Real de Agentes (Real Agent Loop):** Ejecución de inferencia dinámica usando APIs HTTP directas sin intermediarios. Prioridad nativa para la API de **NVIDIA NIM** (`meta/llama-3.1-8b-instruct`) con fallback a **OpenAI** (`gpt-4o-mini`).
* **Tipos de Proyecto Nativos:** Soporte estructurado para 5 tipos de proyectos mediante un registro unificado:
  * 🌐 `web-estatica`: HTML/CSS/JS puro y animaciones.
  * ⚛️ `web-framework`: React, Vue o Vite.
  * 📱 `android-apk`: Compilación con Gradle y despliegue directo en emuladores/dispositivos físicos.
  * 🧩 `chrome-extension`: Extensiones listas para ser cargadas localmente.
  * 🎭 `kinetic-typography`: Animaciones de tipografía cinética interactivas (GSAP, Three.js).
* **Previsualización Nativa Automatizada (`preview_project`):** Herramienta MCP capaz de levantar servidores HTTP, ejecutar scripts de desarrollo (`npm run dev`), instalar y reemplazar APKs sin acumular duplicados (`adb install -r`), y arrancar instancias de Chrome cargando extensiones al instante.
* **Entrevista de Diseño Interactiva (`ask_user`):** Los agentes detienen la ejecución para interrogar interactivamente al usuario sobre tipografías, colores, iconos, animaciones o tipo de proyecto, asegurando que el resultado cumpla con la visión del cliente.
* **Filtros y Seguridad de Contexto:** Protección contra inyección de prompts y Path Traversal guardrails en herramientas del filesystem para evitar que los agentes modifiquen archivos fuera del workspace.
* **Quality Gate Integrado:** Validación estática automática de la sintaxis Python y estructura del proyecto antes de completar cualquier sprint de desarrollo.

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

# Linux / Mac
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (`.env`)
Para que los agentes tengan autonomía real de ejecución e inferencia, crea un archivo `.env` en la raíz del proyecto. El motor prioriza NVIDIA NIM para un procesamiento rápido y potente:

```env
# Clave API de NVIDIA NIM (Recomendada - Prioritaria)
# Consíguela gratis en: https://build.nvidia.com/
NVIDIA_API_KEY=nvapi-tu_clave_aquí

# Clave API de OpenAI (Opcional - Fallback)
OPENAI_API_KEY=sk-proj-tu_clave_aquí

# Configuración de Grafo de Memoria Opcional (Falso por defecto)
USE_GRAPHITI=false
```
*Si no configuras ninguna clave de API, el sistema se ejecutará en **Modo Simulación** de forma gratuita para fines de prueba.*

---

## 💻 Cómo Usarlo

Inicia cualquier flujo de trabajo indicando el `workflow_id` y el nombre de tu proyecto. El runner se encargará de orquestar el ciclo completo de desarrollo:

```bash
python -m runtime.workflow_runner [workflow_id] [nombre_proyecto]
```

### Ejemplos Rápidos:

* **Descubrimiento y Entrevista Inicial:**
  ```bash
  python -m runtime.workflow_runner wf-discovery mi-proyecto-web
  ```
* **Construcción Completa:**
  ```bash
  python -m runtime.workflow_runner wf-build-project mi-dashboard
  ```
* **Auditoría de Calidad y Seguridad:**
  ```bash
  python -m runtime.workflow_runner wf-review mi-app-android
  ```

---

## 🏗️ Arquitectura del Sistema

El workspace se estructura de la siguiente manera:

```
PsychoSv_503/
│
├── 🤖 agents/              → Definición e instrucciones operativas de los agentes
│   ├── psycho-ceo/         → El jefe central: entrevista al usuario y orquesta tareas
│   ├── product-manager/    → Gestiona requisitos y traduce ideas
│   ├── frontend/           → Desarrollo de interfaces visuales e interacciones
│   ├── backend/            → Lógica de servidor, base de datos y APIs
│   ├── qa/                 → Pruebas funcionales e integración
│   ├── security/           → Auditoría de seguridad y dependencias
│   ├── ai-architect/       → Diseña integraciones de inteligencia artificial
│   ├── mcp-architect/      → Diseño y control de herramientas locales
│   └── ...                 
│
├── ⚙️ config/              → Parámetros del sistema y settings
│   └── settings.py         → Carga de variables de entorno y paths del workspace
│
├── 🧠 memory/              → Memoria compartida y persistente
│   ├── active_context.md   → Contexto de trabajo activo del sprint
│   ├── architecture.md     → Registro de decisiones tecnológicas
│   ├── decisions.md        → Historial de elecciones críticas
│   ├── requirements.md     → Requisitos técnicos acordados
│   ├── tasks.md            → Lista de control del proyecto (TODO)
│   ├── lessons_learned.md  → Lecciones aprendidas para evitar regresiones
│   └── sessions/           → Historial de ejecuciones en JSON
│
├── 📋 registry/            → Registros JSON de configuración de la agencia
│   ├── agent-registry.json     → Registro de agentes activos y sus capacidades
│   ├── project-types-registry.json → Registro nativo de tipos de proyectos (NUEVO)
│   ├── mcp-registry.json       → Permisos de herramientas para cada agente
│   └── workflow-registry.json  → Flujos de trabajo y orden de ejecución
│
├── ⚡ runtime/             → El motor de ejecución (Runtime Core)
│   ├── agent_loader.py     → Cargador de agentes e inyector de contexto
│   ├── memory_engine.py    → Manejo de persistencia local (JSON)
│   ├── mcp_executor.py     → Ejecutor autónomo de herramientas MCP (filesystem, cmd, previews)
│   └── workflow_runner.py  → Controlador de bucle interactivo de agentes
│
└── 📐 standards/           → Normas, políticas y leyes internas de la agencia
    ├── constitution.md         → Ley suprema que gobierna a los agentes
    └── coding-standards.md     → Estándares de calidad de código
```

---

## 🤖 Agentes Principales y Jerarquía

| Nivel | Agente | Rol y Responsabilidad | Acceso a Memoria |
| :--- | :--- | :--- | :--- |
| 👑 **Nivel 1** | `psycho-ceo` | Entrevista inicial, orquestación central y previsualización. | Total (Lectura/Escritura) |
| 🎯 **Nivel 2** | `agent-evaluator` | Validador de consistencia y aprobación de entregas. | Lectura/Escritura |
| 🎯 **Nivel 2** | `product-manager` | Estructuración de tareas y especificaciones funcionales. | Lectura/Escritura |
| 💻 **Nivel 3** | `frontend` | Creación de interfaces de usuario y animaciones. | Lectura/Escritura |
| 🔧 **Nivel 3** | `backend` | Arquitectura de datos, lógica de negocio y APIs. | Lectura/Escritura |
| 🚀 **Nivel 3** | `devops` | Scripting de compilación, empaquetado y ADB. | Lectura/Escritura |
| 🔒 **Nivel 3** | `security` | Auditoría de tokens, vulnerabilidades y prompts. | Lectura/Escritura |

---

## 🔄 Flujos de Trabajo (Workflows)

Los workflows coordinan a los agentes secuencialmente para cumplir objetivos globales:

| ID del Workflow | Nombre | Propósito | Secuencia de Agentes |
| :--- | :--- | :--- | :--- |
| `wf-discovery` | Descubrimiento | Capturar la visión del cliente y crear requisitos. | `psycho-ceo` → `product-manager` |
| `wf-planning` | Planificación | Diseñar la estructura del software y dependencias. | `psycho-ceo` → `ai-architect` → `product-manager` |
| `wf-implementation`| Implementación | Escribir código y previsualizar de forma interactiva. | `psycho-ceo` → `frontend` → `backend` → `agent-evaluator` |
| `wf-review` | Revisión | Auditoría técnica profunda antes de la entrega. | `psycho-ceo` → `qa` → `security` → `agent-evaluator` |
| `wf-build-project` | Construcción Completa | Desarrollo completo de extremo a extremo. | `psycho-ceo` → `product-manager` → `ai-architect` → `frontend` → `backend` → `agent-evaluator` |

---

## 🧠 Sistema de Memoria Compartida

El sistema utiliza un modelo de **memoria híbrida** que mantiene la coherencia cognitiva de los agentes en todo momento:

1. **Memoria de Corto Plazo:** Los detalles del turno se mantienen en los mensajes de la sesión del agente.
2. **Memoria de Largo Plazo Local:** Los directorios `memory/sessions/` guardan el historial en archivos JSON.
3. **Memoria de Contexto Central:** Archivos markdown dinámicos (`requirements.md`, `tasks.md`, `active_context.md`) que los agentes leen obligatoriamente antes de ejecutar cualquier acción.
4. **Auto-Learning:** Al final de cada workflow, el subsistema `AutoLearner` extrae errores comunes del Quality Gate y actualiza `memory/lessons_learned.md` de forma autónoma para evitar que los agentes cometan los mismos errores.

---

## 🛠️ Tecnologías Usadas (Tech Stack)

* **Lenguaje:** Python 3.10+
* **LLMs & Inferencia:** NVIDIA NIM (Llama 3.1 8B Instruct) / OpenAI API (GPT-4o mini)
* **Entorno de Visualización:**
  * Servidores Web integrados (Python HTTP Server)
  * Node.js & Vite (para aplicaciones SPA React/Vue)
  * Android Debug Bridge (ADB) + Gradle (para Android APKs)
  * Google Chrome CLI (para extensiones de navegador y previsualización automatizada)
* **Testing:** Pytest & Unittest Mocks

---

## 🗺️ Roadmap / Próximos Pasos

* [ ] Integración nativa de bases de datos vectoriales locales para RAG de documentación.
* [ ] Soporte para emuladores Android basados en Docker en flujos de DevOps.
* [ ] Generación automática de pruebas unitarias por el agente QA mediante Playwright.
* [ ] Interfaz gráfica web interactiva (UI) para la monitorización de los agentes en tiempo real.

---

## 🤝 Contribuir

1. Haz un Fork del proyecto.
2. Crea una rama con tu nueva característica: `git checkout -b feature/nueva-funcion`.
3. Asegúrate de pasar todas las pruebas antes de enviar: `pytest`.
4. Envía un Pull Request detallando los cambios.

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para obtener más información.

---

### Made with ❤️ by [Psycho503](https://github.com/Psycho503DevSv)
