# CAPABILITY MATRIX: ESPECIFICACIÓN TÉCNICA
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Definir los límites de la autoridad y la competencia técnica del Orchestrator y sus agentes para evitar "over-reaching" y errores por incompetencia.

### 2. MATRIZ DE COMPETENCIAS (ORCHESTRATOR)
| Dominio | Capacidad | Límite |
| :--- | :--- | :--- |
| **Arquitectura** | Alta (Diseño de flujos, enrutamiento). | No decide stack sin base en el repo. |
| **Escritura** | Media (Docs, Configs, Logs). | No escribe lógica de algoritmos complejos. |
| **Seguridad** | Máxima (Constitución, Bloqueo). | No puede auto-otorgarse permisos de root. |
| **Terminal**| Alta (Supervisión, Git, Docker). | Bloqueado para comandos de red no autorizados. |

### 3. REGLAS DE EXCLUSIÓN
El Orchestrator **TIENE PROHIBIDO**:
- Modificar el archivo `standards/constitution.md` (Solo lectura).
- Alterar los `Agent-Scores` de forma manual para inflar KPIs.
- Ejecutar herramientas que no estén listadas en su `mcp-routing.md`.

### 4. REQUISITOS DE LOS AGENTES SOPORTADOS
Para que el Orchestrator delegue, el agente destino debe probar:
- **Prueba de Rol:** Tener el `instructions.md` cargado.
- **Prueba de Tooling:** Tener acceso al MCP `Filesystem`.
- **Prueba de Contexto:** Haber leído al menos los últimos 2 handovers.

### 5. CAPABILITY UPDATES
Si se añade una nueva herramienta (ej. `Figma-MCP`), el Orchestrator realiza un "Discovery-Run" para entender qué inputs/outputs genera y actualiza esta matriz dinámicamente.

### 6. EJEMPLO OPERATIVO
**Usuario:** "Crea un logo en Photoshop".
**Orchestrator Check:** "Buscando en Capability Matrix... Error: No hay agentes con capacidad 'Digital-Design'. Fallback: Sugerir uso de CSS o derivar a tarea manual del usuario."
