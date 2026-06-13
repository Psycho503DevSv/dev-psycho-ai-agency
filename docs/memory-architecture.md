# ARQUITECTURA DE MEMORIA (MEMORY ARCHITECTURE)

## 1. ESTRATEGIA DE CAPAS (TIERED MEMORY)
- **Capa 1: Hot Memory (Sesión):** Estado del chat actual. Se archiva en `memory/sessions/` al finalizar.
- **Capa 2: Project Memory (Directa):** Datos específicos en `memory/projects/`. Alta relevancia para especialistas.
- **Capa 3: Core Memory (Global):** `/registry/` y `/standards/`. Leyes y capacidades.
- **Capa 4: Deep Memory (Histórica):** `memory/lessons-learned/` y `memory/decisions/`.

## 2. ESTRATEGIA DE INDEXACIÓN Y RECUPERACIÓN
- **Naming Convention:** `YYYY-MM-DD_[PROYECTO|AGENTE]_[ETIQUETA].md`.
- **Búsqueda:** Los agentes deben priorizar la búsqueda semántica sobre la jerarquía de carpetas.
- **Recuperación:** El Knowledge Manager es el encargado de des-duplicar información y consolidar "Patrones Reutilizables".

## 3. ESTRATEGIA DE APRENDIZAJE Y ARCHIVADO
- **Feedback Loop:** Cada vez que el Project Manager marca un hito como "Completado", el Knowledge Manager debe extraer 3 lecciones aprendidas (1 éxito, 1 fallo, 1 mejora).
- **Archivado:** Proyectos inactivos por más de 12 meses se comprimen y mueven a `/memory/vault/`.

---
*Referencia: memory/memory-governance.md*
