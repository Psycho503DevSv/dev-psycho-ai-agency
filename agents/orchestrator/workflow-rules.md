# WORKFLOW RULES: MÁQUINA DE ESTADOS FINITOS
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Regular las interacciones entre agentes y definir los "Estados Legales" por los que puede pasar el sistema.

### 2. ESTADOS DEL SISTEMA (SYSTEM STATES)
- **S0 - IDLE:** Esperando input del usuario.
- **S1 - DISCOVERY:** Analizando requisitos y archivos.
- **S2 - PLANNING:** Construyendo o ajustando el Roadmap.
- **S3 - DEVELOPMENT:** Agentes especialistas escribiendo código.
- **S4 - VALIDATION:** Pasando Quality Gates y tests.
- **S5 - DEPLOY/RELEASE:** Finalizando cambios y documentando.
- **S_ERR - RECOVERY:** Ejecutando protocolos de fallo.

### 3. REGLAS DE TRANSICIÓN
1. No se puede pasar de S1 a S3 sin pasar por S2 (Planificación obligatoria).
2. Si un agente en S3 reporta un error crítico, el sistema transiciona a S_ERR.
3. El retorno de S_ERR debe ser al estado anterior al fallo, nunca a S0 (a menos que sea irrecuperable).

### 4. GESTIÓN DE COLAS (CONCURRENCY RULES)
- **Prioridad de Ejecución:** Tareas de Seguridad > Tareas de Infraestructura > Funcionalidades > Documentos.
- **Deadlock Prevention:** Si la Tarea A espera a B y B espera a A, el Orchestrator fuerza la finalización de A (Asignando valores por defecto) para desbloquear a B.

### 5. EVENTOS DISPARADORES (TRIGGERS)
- `USER_PROMPT` $\rightarrow$ Entrar en S1.
- `ROADMAP_READY` $\rightarrow$ Entrar en S3.
- `FILES_CHANGED` $\rightarrow$ Activar S4 automáticamente.
- `TESTS_PASSED` $\rightarrow$ Avanzar en el Roadmap.

### 6. EJEMPLO OPERATIVO
**Situación:** El `Frontend-Engineer` termina su tarea pero los tests fallan.
**Transición:** S3 (Development) $\rightarrow$ S4 (Validation) $\rightarrow$ [Failure Detected] $\rightarrow$ S_ERR (Recovery) $\rightarrow$ Retorno a S3 (con feedback de error).
