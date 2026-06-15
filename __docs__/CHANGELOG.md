# Registro de Cambios (CHANGELOG)

Todos los cambios notables realizados en el framework PsychoSv_503 AI DevOS están documentados en este archivo.

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
