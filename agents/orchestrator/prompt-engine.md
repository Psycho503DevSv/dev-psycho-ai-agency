# PROMPT ENGINE: METAPROMPTING Y REFINAMIENTO
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Optimizar las instrucciones enviadas a los sub-agentes para maximizar la tasa de éxito y minimizar la fricción comunicativa.

### 2. ARQUITECTURA DEL PROMPT (THE INJECTION)
Todo prompt generado por el Orchestrator para un especialista debe contener:
1. **Contexto de Rol:** Definición breve pero autoritaria.
2. **Input Payload:** JSON con archivos y variables.
3. **Restricciones Técnicas:** Qué NO usar.
4. **Contrato de Salida esperado:** Respuesta estructurada.
5. **Enlace a la Constitución:** Cláusulas relevantes para la subtarea.

### 3. FORMULACIÓN DINÁMICA
| Situación | Técnica de Prompting | Ejemplo |
| :--- | :--- | :--- |
| Tarea Compleja | **Zero-Shot + COT** | "Define paso a paso tu razonamiento antes de editar." |
| Refactorización | **Few-Shot (Ejemplos)** | "Sigue este patrón: [Ejemplo A] -> [Ejemplo B]." |
| Debugging | **Verification Prompting** | "Lee el log, identifica la línea y confirma la causa raíz." |

### 4. REGLAL DE REFINAMIENTO (ITERACIÓN)
Si un agente devuelve un resultado pobre:
- El `Prompt-Engine` analiza si la instrucción original fue ambigua.
- Genera un `Clarification-Prompt` con ejemplos correctores.
- Inyecta una advertencia de "Prioridad Crítica" en el siguiente turno.

### 5. CASO DE ERROR: "INSTRUCTION OVERLOAD"
- **Problema:** El prompt es tan largo que el agente empieza a alucinar.
- **Solución:** Dividir el prompt en 2 partes: Una de "Setup" y otra de "Acción Directa".

### 6. EJEMPLO OPERATIVO
**Generando para AI-Engineer:**
"Eres AI-Engineer. Tu objetivo es mapear [db.schema] a [models.py]. No uses librerías externas fuera de SQLAlchemy. Salida: Solo el contenido del archivo models.py entre tags de código."
