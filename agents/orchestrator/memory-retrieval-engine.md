# MEMORY RETRIEVAL ENGINE: RAG OPERACIONAL
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Optimizar la recuperación de información desde las capas L3, L4 y L5 mediante técnicas de búsqueda híbrida (Semántica + Léxica).

### 2. ESTRATEGIA DE BÚSQUEDA HÍBRIDA
1. **Búsqueda Léxica (Exacta):** Para nombres de funciones, variables y errores específicos (Status 404, variable `user_db`).
2. **Búsqueda Semántica:** Para conceptos vagos ("¿Cómo manejábamos la sesión en el último proyecto?").
3. **Búsqueda Temporal:** Priorizar registros de memoria más recientes en caso de conflictos.

### 3. ALGORITMO DE RANKING DE RESULTADOS
Ponderar los resultados de búsqueda según:
- **Match de Tecnología:** Si el proyecto actual es Node.js, filtrar recuerdos de Python.
- **Autoría:** Recuerdos generados por el Administrador > Recuerdos generados por agentes automáticos.
- **Validación:** ¿La lección recuperada fue validada con `Success` anteriormente?

### 4. PROCESO DE INTEGRACIÓN (INJECTION)
Una vez recuperado el dato:
- No inyectar el bloque de memoria completo.
- Extraer solo la **Lección Accionable** (Refined Knowledge).
- Formato: `[MEMORY_HINT: En el proyecto X, el driver Y fallaba por Z. Se recomienda usar la config W.]`

### 5. CASO DE ERROR: "MEMORY NOISE"
- **Problema:** La búsqueda devuelve 50 resultados vagos.
- **Solución:** Aumentar el umbral de similitud de 0.7 a 0.9 y requerir que el usuario aporte una keyword manual.

### 6. AUTO-OPTIMIZACIÓN
Si el Orchestrator recupera una memoria y el resultado de la tarea es un `FAILURE`, el motor marca esa memoria con un flag de `LOW_QUALITY` para que no sea seleccionada de nuevo para tareas similares.
