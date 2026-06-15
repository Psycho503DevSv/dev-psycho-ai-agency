# Arquitectura de Datos y Memoria Semántica

Este documento describe la estructura y el almacenamiento de datos persistentes y memorias semánticas dentro del sistema.

## 1. Memoria Local en Archivos JSON

Por defecto, PsychoSv_503 AI DevOS almacena las memorias en la carpeta `memory/` organizada de la siguiente manera:

```text
memory/
├── global/
│   └── global_patterns.json  # Patrones y conocimientos promovidos globalmente
└── sessions/
    └── <id-sesión-workflow>/
        └── memories.jsonl    # Log cronológico de eventos e informes de la sesión
```

### Estructura de un Evento de Memoria Local
Cada entrada en `memories.jsonl` es un objeto JSON que representa un paso ejecutado:
```json
{
  "timestamp": "2026-06-15T12:00:00.123456",
  "category": "workflow_step",
  "data": {
    "project": "proyecto-demo",
    "step": "backend",
    "status": "success",
    "role": "backend",
    "output": "Salida detallada del agente..."
  }
}
```

## 2. Memoria Semántica de Grafos (Neo4j / Graphiti)

Cuando `USE_GRAPHITI=true` en `.env`, el sistema utiliza `GraphitiBridge` para inicializar y guardar información en una base de datos Neo4j.

### Esquema y Relaciones Semánticas
Graphiti construye un grafo jerárquico dinámico basado en:
* **Entidades (Nodos):** Agentes, Archivos, Tecnologías, Requisitos, Errores.
* **Episodios:** Eventos temporales que disparan la creación y conexión de entidades.
* **Relaciones (Bordes):** `EJECUTA`, `DEPENDE_DE`, `MODIFICA`, `CONTIENE`, `RESUELVE`.

Esto permite realizar búsquedas complejas para recuperar qué agente modificó cierto archivo de configuración o qué dependencias causaron errores en workflows anteriores.

---
*Actualizado por: RAG-Architect | Fecha: 2026-06-15*
