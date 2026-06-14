# Lessons Learned & Optimization History

## System Wide Lessons
- **Context Injection:** Injecting the entire memory folder causes rapid token consumption and agent confusion. Keep context narrow and role-specific.
- **Verification Loop:** All specialist outputs must be vetted by a quality/evaluator agent to prevent code regressions and architectural drifts.
- **Sintaxis Correcta:** Validar la sintaxis de todos los archivos antes de dar por completado un cambio. Error reportado: `SYNTAX_ERROR: app.py - invalid syntax (L12)`.
* Verifica la sintaxis del código en cada paso del desarrollo para evitar errores de compilación.
* Utiliza herramientas de análisis de código para detectar errores de sintaxis antes de la ejecución.
* Realiza pruebas unitarias y de integración para asegurarse de que el código cumpla con los requisitos de calidad.
