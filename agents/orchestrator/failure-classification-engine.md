# FAILURE CLASSIFICATION ENGINE: TAXONOMÍA DE ERRORES
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Analizar cada fallo del sistema para identificar patrones, diagnosticar causas raíz y aplicar la estrategia de recuperación adecuada.

### 2. TAXONOMÍA DE ERRORES DE DEVOS

| Código | Categoría | Causa Probable | Severidad |
| :--- | :--- | :--- | :---: |
| **ERR_CORE_01** | Herramienta | MCP Connection lost, Timeout. | 2 |
| **ERR_LOGIC_02** | Alucinación | El agente miente sobre el estado del FS. | 4 |
| **ERR_SEC_03** | Seguridad | Intento de acceso a archivo restringido / secrets. | 5 (Crítica) |
| **ERR_ARCH_04** | Diseño | Incompatibilidad de librerías o stack. | 3 |
| **ERR_USER_05** | Input | Instrucción ambigua o contradictoria. | 1 |

### 3. PROTOCOLO DE DIAGNÓSTICO
1. **Captura:** Recoger el log de error exacto de la terminal o el pipeline.
2. **Context Check:** Ver qué archivos se estaban editando y qué agentes estaban activos.
3. **Clasificación:** Asignar un código de la tabla anterior.
4. **Action:** Disparar el módulo correspondiente del `recovery-protocol.md`.

### 4. ANÁLISIS DE REPETICIÓN
Si un error `ERR_LOGIC_02` ocurre 3 veces seguidas:
- El motor concluye que el **Prompt** es el problema.
- Dispara una re-escritura de instrucciones vía `Prompt-Engine`.

### 5. REGISTRO DE TELEMETRÍA
Cada fallo se guarda en `memories/session/telemetry_log.json` para análisis post-mortem por parte del Orchestrator al final de la jornada.

### 6. EJEMPLO OPERATIVO
**Error:** `npm install` falla por falta de espacio en disco.
**Motor:** Clasificado como `ERR_CORE_01`. Causa: Infraestructura. 
**Acción:** No re-intentar código. Notificar al usuario sobre limpieza de disco o cambio de partición.
