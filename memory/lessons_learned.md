# Lessons Learned & Optimization History

## System Wide Lessons
- **Context Injection:** Injecting the entire memory folder causes rapid token consumption and agent confusion. Keep context narrow and role-specific.
- **Verification Loop:** All specialist outputs must be vetted by a quality/evaluator agent to prevent code regressions and architectural drifts.
- **Sintaxis Correcta:** Validar la sintaxis de todos los archivos antes de dar por completado un cambio. Error reportado: `SYNTAX_ERROR: app.py - invalid syntax (L12)`.
* Verifica la sintaxis del código en cada paso del desarrollo para evitar errores de compilación.
* Utiliza herramientas de análisis de código para detectar errores de sintaxis antes de la ejecución.
* Realiza pruebas unitarias y de integración para asegurarse de que el código cumpla con los requisitos de calidad.
* Verifica la existencia de archivos obligatorios (README.md, requirements.txt) en el workflow.
* Asegúrate de incluir los archivos necesarios en el control de versiones (git) para evitar errores de calidad.
* Revisa la configuración del QualityGate para asegurarte de que se estén evaluando los archivos correctos.
* Asegúrate de incluir un archivo `README.md` en el proyecto.
* Verifica la presencia de un archivo `requirements.txt` en el proyecto.
* Revisa la configuración del Workflow `wf-qg` para asegurarte de que incluya las comprobaciones de archivos necesarios.
* Verifica la existencia de archivos obligatorios como README.md y requirements.txt antes de iniciar el workflow.
* Asegúrate de que los archivos requeridos estén en el directorio correcto y no estén omitidos.
* Revisa la configuración del workflow para asegurarte de que esté incluyendo la validación de archivos obligatorios.
* Verifica la existencia de archivos obligatorios (README.md y requirements.txt) antes de iniciar el flujo de trabajo.
* Asegúrate de que los archivos obligatorios estén en el directorio correcto y no estén omitidos en el flujo de trabajo.
* Revisa la configuración de calidad del flujo de trabajo (wf-qg) para asegurarte de que esté incluyendo la validación de archivos obligatorios.
* Verificar la presencia de archivos obligatorios (README.md, requirements.txt) en el proyecto.
* Implementar validaciones de calidad para detectar faltantes de archivos importantes.
* Revisar y actualizar el workflow (wf-qg) para incluir comprobaciones de archivos necesarios.
* Verifica la presencia de archivos obligatorios (README.md, requirements.txt) en el proyecto.
* Implementa un validador de calidad que busque archivos faltantes en el proyecto.
* Documenta los archivos obligatorios en el proyecto para evitar confusiones en el futuro.
