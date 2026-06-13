# CONTEXT PRIORITY ENGINE: CALIFICACIÓN DE RELEVANCIA
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Asignar un puntaje de relevancia (0-1.0) a cada pieza de información en el contexto para decidir qué se queda y qué se va durante una purga.

### 2. FACTORES DE PONDERACIÓN ($W_{rel}$)
1. **Recency (Tiempo):** ¿Qué tan reciente es la información? (Peso: 30%).
2. **Task Linkage (Vínculo):** ¿Está directamente relacionada con la `Current_Task_ID`? (Peso: 50%).
3. **Symbol Centrality:** ¿Contiene definiciones de funciones o variables core del proyecto? (Peso: 20%).

### 3. MATRIZ DE PRIORIDAD OPERATIVA
| Rango Score | Acción en Purga | Ejemplo |
| :--- | :--- | :--- |
| **0.9 - 1.0** | Inmune | Constitución, Requisito Actual. |
| **0.7 - 0.8** | Mantener Intacto | Código fuente abierto actualmente. |
| **0.4 - 0.6** | Resumir | Conversaciones pasadas, logs de build. |
| **< 0.4** | Eliminar | Saludos, intros, comandos de navegación básicos. |

### 4. REGLAL DE ORO: EL "KERNEL" DE CONTEXTO
Siempre debe haber un espacio reservado (15% de la ventana) para la Constitución y los `Instructions.md` del Orchestrator. Estos nunca entran en el proceso de calificación de relevancia; su prioridad es absoluta (1.1).

### 5. CASO DE USO: CAMBIO DE CONTEXTO
Si el usuario de repente cambia de "Backend" a "DevOps":
- El motor detecta el cambio de `Task_Linkage`.
- La información de Backend baja su score global de 0.9 a 0.3.
- Se ejecuta un `context-management.md` inmediato para liberar espacio para las nuevas herramientas de DevOps.

### 6. EJEMPLO DE METADATA (INTERNO)
`File: [auth.js], Priority: 0.95 (Active Editor), Memory_Tier: Working`
`File: [package-lock.json], Priority: 0.2 (Noise), Memory_Tier: Project`
