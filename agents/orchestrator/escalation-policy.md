# ESCALATION POLICY: GOBERNANZA HUMANA
## AI DevOS Orchestrator Module

### 1. OBJETIVO
Definir con precisión matemática cuándo el Orchestrator debe renunciar a su autonomía y solicitar intervención, juicio o permisos del Usuario.

### 2. DISPARADORES DE ESCALAMIENTO (THRESHOLD)
Se escala si:
- **Incertidumbre Lógica:** $P(Success) < 0.6$.
- **Riesgo Crítico:** $S_R > 0.7$ (según `risk-analysis-engine.md`).
- **Bloqueo Herramienta:** 2 fallos consecutivos de una herramienta vital.
- **Conflicto Ético:** Violación de la Constitución.
- **Coste de Recursos:** Tarea estimada en > 15k tokens de un solo paso.

### 3. PROTOCOLO DE PREGUNTA (USER_CONSULT)
Al escalar, el Orchestrator debe evitar preguntas abiertas. Debe seguir el formato:
1. **Dato Técnico:** "Fallo en la conexión a la DB PostgreSQL".
2. **Contexto:** "Las credenciales en `.env` parecen ser incorrectas".
3. **Opciones:**
   - **A:** Probar con credenciales por defecto. (Poco seguro).
   - **B:** Pedir al usuario que ingrese las credenciales correctas. (Seguro).
4. **Recomendación:** "Sugiero la Opción B para mantener la integridad."

### 4. MODOS DE AUTONOMÍA (LEVELS)
| Nivel | Nombre | Descripción |
| :--- | :--- | :--- |
| **L0** | Read-Only | El sistema solo analiza, no propone cambios. |
| **L1** | Shadow | Propone cambios pero no ejecuta nada. |
| **L2** | Pilot | Ejecuta cambios en archivos de texto, escala en terminal. |
| **L3** | Full Auto | Ejecuta todo, escala solo en Riesgo Crítico. |

### 5. CASO LÍMITE: "SILENT FAILURE"
Si el sistema detecta que está escalando demasiado seguido (> 3 veces por hora para tareas simples):
- El motor concluye que hay un "Gap de Conocimiento" masivo.
- Acción: Pide al usuario sesión de `Knowledge-Inference` (lectura masiva de docs/repo).

### 6. REGISTRO DE DECISIONES
Toda respuesta del usuario en un escalamiento se guarda como una **Directiva de Preferencia** en la Memoria L4, influyendo en futuras decisiones del `decision-engine.md`.
