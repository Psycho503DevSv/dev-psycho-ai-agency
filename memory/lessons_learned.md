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
* Verifica la existencia de archivos obligatorios (README.md y requirements.txt) antes de iniciar el workflow.
* Asegúrate de que los archivos mencionados en el error estén en el directorio correcto y no estén omitidos en el código.
* Revisa la configuración del QualityGate para asegurarte de que los archivos obligatorios estén incluidos en la lista de verificación.
* Verifica la presencia de archivos obligatorios (README.md, requirements.txt) en el workflow.
* Asegúrate de que el archivo README.md esté presente en el repositorio.
* Revisa la configuración del workflow para asegurarte de que se estén revisando los archivos requeridos.
* Asegúrate de incluir un archivo README.md en el proyecto.
* Verifica la existencia de un archivo requirements.txt en el proyecto.
* Revisa la configuración del Workflow para asegurarte de que esté completo y correcto.
* Verifica la existencia de archivos obligatorios (README.md, requirements.txt) en el proyecto antes de iniciar la validación.
* Asegúrate de que los archivos obligatorios estén actualizados y no estén faltando en el repositorio.
* Revisa la configuración del Workflow (wf-qg) para asegurarte de que incluya la validación de los archivos obligatorios.
* No olvides agregar un archivo requirements.txt con las dependencias necesarias.
* Verifica que todos los archivos requeridos estén presentes en el proyecto.
* Verifica la integridad del proyecto antes de enviarlo a QualityGate.
* Verifica que todos los archivos requeridos estén presentes en el proyecto antes de enviarlo a QualityGate.
* Revisa la lista de errores de QualityGate antes de considerar el workflow como finalizado.
* Verifica que todos los archivos obligatorios estén presentes antes de ejecutar el Workflow wf-qg.
* Verifica la presencia de archivos obligatorios (README.md y requirements.txt) en el workflow.
* Asegúrate de que el workflow (wf-qg) esté configurado correctamente para detectar archivos faltantes.
* Revisa la documentación del workflow para entender qué archivos y configuraciones son requeridas para su ejecución.
* Verificar la presencia de archivos obligatorios (README.md, requirements.txt) antes de iniciar el workflow.
* Implementar validaciones de calidad para detectar archivos faltantes en el código.
* Revisar la configuración del QualityGate para asegurarse de que esté chequeando los archivos obligatorios.
* Verifica la existencia de archivos obligatorios (README.md, requirements.txt) en el proyecto antes de iniciar el workflow.
* Verifica la presencia de archivos obligatorios (README.md, requirements.txt) antes de iniciar el workflow.
* Asegúrate de que los archivos requeridos estén actualizados y no faltantes.
* Revisa la configuración del workflow para asegurarte de que se estén evaluando los archivos correctos.
* Es importante proporcionar información de entrada clara para evitar preguntas generales innecesarias.
* Es fundamental coordinar con el equipo para asegurar la alineación del alcance del proyecto.
* La documentación debe ser actualizada en tiempo real para reflejar los cambios en el alcance del proyecto.
* Verificar la ruta absoluta y el nombre del archivo antes de utilizar herramientas de lectura o escritura de archivos.
* Utilizar herramientas de gestión de flujo de trabajo como Bash para definir y ejecutar tareas de manera automática.
* Verificar el acceso al directorio antes de ejecutar comandos que requieran permisos elevados.
* Verifica la existencia de archivos de requerimientos antes de iniciar el flujo de trabajo.
* Asegúrate de que los archivos de requerimientos estén en el lugar correcto y sean accesibles para el validador de calidad.
* Revisa la configuración del validador de calidad para asegurarte de que esté configurado correctamente para buscar archivos de requerimientos en el lugar adecuado.
