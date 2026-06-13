# OUTPUT CONTRACTS: ESQUEMAS DETERMINISTAS
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Garantizar que toda comunicación del sistema sea predecible, parseable por otros agentes y profesional para el Usuario.

### 2. CONTRATOS POR DESTINATARIO

#### A. Contrato de Usuario (Executive Level)
- **Tono:** Directo, proactivo, técnico.
- **Componentes:**
  - `Summary`: Qué se hizo.
  - `Evidence`: Links a archivos modificados.
  - `Milestone Status`: % del proyecto completado.
  - `Call to Action`: Siguiente decisión requerida.

#### B. Contrato de Agente (Technical Level)
- **Formato:** JSON/XML/Markdown estructurado.
- **Componentes:** `Task_ID`, `Command`, `Env_Vars`, `Input_Files`, `Exit_Condition`.

#### C. Contrato de Sistema (Telemetry Level)
- **Formato:** JSON Log.
- **Componentes:** `Timestamp`, `Severity`, `Module_ID`, `Message`, `Internal_State`.

### 3. REGLAS DE FORMATEO (STRICT)
- **Paths:** Siempre absolutos o relativos al root con link markdown: `[src/main.ts](src/main.ts)`.
- **Errores:** Seguir la taxonomía del `failure-classification-engine.md`.
- **Acciones:** Usar verbos de acción (Creado, Editado, Borrado, Auditado).

### 4. VALIDACIÓN DE SALIDA (PRE-FLIGHT)
Antes de imprimir:
1. ¿Hay placeholders? (Si sí $\rightarrow$ Cancelar y completar).
2. ¿Los links funcionan? (Si no $\rightarrow$ Corregir).
3. ¿El idioma es el correcto?

### 5. CASO DE ERROR: "MALFORMED OUTPUT"
Si un agente envía un output que no sigue su contrato (ej. olvida los links de evidencia):
- El Orchestrator rechaza el mensaje internamente.
- Pide al agente "Re-formatear salida según Contrato B".
- No muestra este error al Usuario a menos que persista.

### 6. EJEMPLO DE MENSAJE FINAL
```markdown
# ✅ Hito de Seguridad Completado
He finalizado la auditoría de los endpoints de la API.

**Cambios Clave:**
- Añadido rate-limiting en [server/index.js](server/index.js#L20).
- Corregida vulnerabilidad de inyección en [db/query.js](db/query.js#L55).

**Próximo Paso Sugerido:** Proceder a ejecutar el workflow de Tests E2E con Playwright. ¿Deseas continuar?
```
