# RECOVERY PROTOCOL: AUTOCURACIÓN SISTÉMICA
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Definir las trayectorias de recuperación ante fallos técnicos para que el sistema mantenga su operatividad sin requerir reinicios manuales constantes.

### 2. ALGORITMO DE RECOVERY (BACK-OFF & DIVERGE)
Cuando ocurre un fallo (según `failure-classification-engine.md`):

#### Nivel 1: Re-intento Local (Retry)
- **Condición:** Error transitorio de herramienta (timeout).
- **Acción:** Re-ejecutar el mismo comando una vez con el doble de tiempo de espera.

#### Nivel 2: Cambio de Estrategia (Diverge)
- **Condición:** El comando es correcto pero el entorno falla (ej. una librería no instala).
- **Acción:** Buscar una herramienta alternativa en `tool-selection-engine.md`. (Ej. pasar de `npm` a `yarn` o editar el archivo manualmente).

#### Nivel 3: Rollback de Estado
- **Condición:** El cambio técnico rompió el sistema o no pasa los tests.
- **Acción:** Ejecutar `git checkout -- .` o restaurar archivos desde la memoria de sesión L2.

#### Nivel 4: Amnesia Parcial
- **Condición:** El agente está en un bucle lógico infinito.
- **Acción:** Borrar el historial de los últimos 2 turnos de ese agente y re-enviar el handover con una prohibición explícita de la acción fallida.

### 3. RECOVERY MATRIX
| Fallo | Acción Inmediata | Escalado |
| :--- | :--- | :--- |
| Error de Sintaxis | Autocorrección vía Linter. | Re-enviar a Agente. |
| Test Fallido | Leer log de error + Re-editar. | Marcar como `BLOCKED`. |
| MCP unreachable | Health check del host. | Notificar al Usuario. |
| Memory Corrupted | Re-indexado desde Git/FS. | Ignorar L3, usar L1. |

### 4. REGLAL DE ORO
Nunca intentar una recuperación que pueda borrar el trabajo del Usuario en otros archivos no relacionados. El radio de impacto del recovery debe estar confinado a la `Current_Task`.

### 5. EJEMPLO OPERATIVO
**Error:** `Backend-Engineer` borró accidentalmente el `index.html` mientras trabajaba en el CSS.
**Orchestrator Recovery:**
1. Detecta archivo faltante en Quality Gate.
2. Ejecuta `git checkout src/index.html`.
3. Informa: "Restaurado index.html eliminado por error técnico del agente de Frontend."
