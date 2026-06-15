# Registro de Cambios (CHANGELOG)

Todos los cambios notables realizados en el framework PsychoSv_503 AI DevOS están documentados en este archivo.

## [1.2.0] - 2026-06-15

### Añadido (Fase 1: Estabilidad y Robustez)
* **Reintentos con Backoff Exponencial (`_call_llm`):** Las llamadas al LLM se reintentan automáticamente hasta 3 veces con backoff exponencial (2s, 4s, 8s) ante errores de red o rate-limits. Nunca más caídas silenciosas.
* **Parser JSON Auto-Correctivo (`_parse_tool_call`):** Nuevo método dedicado al parseo de tool calls. Soporta bloques ` ```json ```, ` ``` ` sin etiqueta y JSON crudo. Aplica 4 correcciones automáticas cuando el LLM alucina comillas simples, comas sobrantes o booleanos de Python.
* **Detección de Bucles de Alucinación:** Si un agente repite la misma respuesta dos veces consecutivas se corta el bucle inmediatamente. Si invoca la misma herramienta con los mismos argumentos 3+ veces se aborta con log de error.
* **Autocorrección de JSON Inválido en Tiempo Real:** Cuando el agente intenta invocar una herramienta pero el JSON no es válido, el runner devuelve un mensaje de error correctivo al LLM para que lo reformatee, sin desperdiciar turnos ni tokens.
* **Mocks de LLM en Testing (`tests/test_kernel.py`):** Todas las llamadas reales al LLM en `test_workflow_runner` y `test_workflow_runner_edge_cases` ahora están mockeadas con `unittest.mock.patch`. El tiempo de ejecución de la suite cayó de **2m 15s → 9.36 segundos** sin necesidad de API keys ni internet.

## [1.1.0] - 2026-06-15

### Añadido
* **Registro de Tipos de Proyecto Nativos (`registry/project-types-registry.json`):** Registro con especificaciones de 5 tipos de proyecto soportados por la agencia (`web-estatica`, `web-framework`, `android-apk`, `chrome-extension`, `kinetic-typography`) detallando sus herramientas de construcción, servidores de desarrollo, estrategias de previsualización y agentes asignados.
* **Herramienta de Previsualización Nativa MCP (`preview_project`):** Implementada en `runtime/mcp_executor.py` para permitir la apertura automática de servidores locales HTTP, servidores de desarrollo en background, instalación/reemplazo de APKs sin duplicados (`adb install -r`), y la apertura de Chrome con extensiones cargadas.
* **Pruebas de Previsualización:** Agregados casos de prueba a la suite de tests en `tests/runtime/test_mcp_executor.py` cubriendo tipos de proyecto soportados y manejo de errores.

### Modificado
* **Instrucciones de CEO (`agents/psycho-ceo/instructions.md`):** Modificadas para exigir preguntar primero por el tipo de proyecto en la entrevista inicial y para previsualizar el código después de cada bloque funcional.

## [1.0.0] - 2026-06-15

### Añadido
* **Bucle Real de Agentes (Real Agent Loop):** Implementación de llamadas dinámicas a modelos LLM utilizando APIs HTTP (NVIDIA NIM como prioridad principal y OpenAI como fallback).
* **Ejecutor MCP Local (`runtime/mcp_executor.py`):** Un despachador autónomo que permite realizar operaciones seguras en el filesystem (`read_file`, `write_file`, `list_dir`) y ejecutar comandos locales en consola (`run_command`).
* **Suite de Pruebas Unitarias completas:** Añadida cobertura de pruebas con `tests/runtime/test_mcp_executor.py` y correcciones en `tests/test_kernel.py` alcanzando 16 de 16 pruebas exitosas.
* **Documentación Centralizada (`__docs__/`):** Creación de la estructura de documentación en el workspace de desarrollo incluyendo arquitectura, instalación, API, base de datos y seguridad.
* **Entrevista Interactiva (`ask_user`):** Implementada la herramienta MCP `ask_user` que detiene la ejecución para interrogar interactivamente al usuario sobre detalles de diseño (iconos, fondos, animaciones) e integradas directivas de entrevista obligatoria en `psycho-ceo` y `product-manager`.

### Modificado
* **Traducción al Español de Instrucciones:** Traducidas al español las instrucciones de todos los 16 agentes en `agents/*/instructions.md` y guías técnicas principales.
* **Integración del Quality Gate:** El validador estático ahora se ejecuta dinámicamente y se integra con el ciclo de Auto-Learning.

---
*Actualizado por: Project Manager Agent | Fecha: 2026-06-15*
