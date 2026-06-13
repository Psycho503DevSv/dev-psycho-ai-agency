# TASK DECOMPOSITION ENGINE: ATOMIZACIÓN
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Convertir requisitos ambiguos de alto nivel en una serie de tareas atómicas, trazables y ejecutables por agentes especialistas.

### 2. ALGORITMO DE DESCOMPOSICIÓN (HTN)
1. **Analizar Estado Final:** ¿Cómo se ve el éxito (Definition of Done)?
2. **Dividir por Áreas de Dominio:** 
   - UI/UX
   - Business Logic
   - Database / Data Layer
   - Infrastructure / DevOps
3. **Asignar Dependencias:** Determinar qué tareas bloquean a otras (Ruta Crítica).
4. **Validar Atomicidad:** Si una tarea requiere > 30 mins de un agente, se debe seguir descomponiendo.

### 3. MATRIZ DE ESTRUCTURACIÓN DE TAREAS
| Campo | Requisito | Propósito |
| :--- | :--- | :--- |
| **ID** | `T-001` | Seguimiento en el Roadmap. |
| **Owner** | Agent_ID | Responsabilidad única. |
| **Prerequisites** | [ID_Tarea] | Control de flujo paralelizable. |
| **Output expected** | Artifact URI | Validación automática. |

### 4. CASOS LÍMITE
- **Tarea Indivisible:** El requisito es una única línea de código crítica.
    - *Acción:* Tratar como tarea de `Security Review` antes que de implementación.
- **Dependencia Circular:** El diseño de DB depende del Frontend y viceversa.
    - *Acción:* Forzar una fase de `Architecture Prototype` (Nivel 2) para romper el ciclo.

### 5. EJEMPLO OPERATIVO
**Requisito:** "Pon un chat en tiempo real en la web".
**Decomposition:**
1. `T-001`: Setup de Socket.io en el servidor (Backend-Engineer).
2. `T-002`: Crear componente de chat en React (Frontend-Engineer).
3. `T-003`: Integrar cliente con servidor (Frontend-Engineer).
4. `T-004`: Test de latencia y concurrencia (QA-Engineer).
