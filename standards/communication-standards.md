# ESTÁNDARES DE COMUNICACIÓN Y POLÍTICA DE IDIOMA

## 1. POLÍTICA DE IDIOMA OFICIAL
El **Español** es el idioma oficial y obligatorio para todas las interacciones dentro del AI DevOS.

### 1.1 Reglas de Oro
- **Interacción con el Usuario:** Todas las respuestas, preguntas y sugerencias deben ser en español.
- **Documentación Técnica:** READMEs, CHANGELOGs, diagramas y manuales deben redactarse en español.
- **Logs y Reportes:** Los resúmenes de ejecución y logs de actividad deben ser legibles en español.
- **Análisis de Fuentes:** Si un agente consulta documentación en inglés, debe traducirla mentalmente y presentar los hallazgos en español.

### 1.2 Excepciones Técnicas
Se permite el uso del inglés exclusivamente para:
- Sintaxis de código fuente (variables, funciones, clases).
- Nombres de APIs, métodos de protocolos (ej. MCP) y librerías.
- Archivos de configuración técnica (ej. `.env`, `Dockerfile`).

## 2. PROTOCOLOS DE COMUNICACIÓN ENTRE AGENTES
La comunicación debe ser estructurada y libre de ambigüedad para maximizar la eficiencia del contexto.

### 2.1 El Formato de "Handover" (Entrega de Tareas)
Cuando un agente transfiere el control a otro, debe incluir:
1. **Contexto:** ¿Qué se ha hecho hasta ahora?
2. **Objetivo:** ¿Qué debe hacer el siguiente agente específicamente?
3. **Restricciones:** ¿Qué no debe hacer o qué límites existen?
4. **Archivos Relacionados:** Enlaces (links de Markdown) a los archivos pertinentes.

### 2.2 Tono y Estilo
- **Profesional y Directo:** Evitar florituras innecesarias.
- **Asertivo:** Si algo es incorrecto o riesgoso, declararlo claramente.
- **Estructurado:** Uso extensivo de listas, tablas y jerarquías Markdown.

## 3. GESTIÓN DE ERRORES Y ALERTAS
- **Claridad ante todo:** No emitir "Error 500". Emitir "Error de Conexión en MCP Database al intentar leer el esquema".
- **Sugerencia de Solución:** Cada reporte de error debe ir acompañado de una posible vía de resolución.

## 4. CASOS DE USO Y BUENAS PRÁCTICAS
- **Mal ejemplo:** "Task done. Next agent start working."
- **Buen ejemplo:** "Fase de Descubrimiento finalizada. Se han recolectado 5 requisitos funcionales en `memory/projects/alpha/reqs.md`. Agente Arquitecto: procede a diseñar el esquema de base de datos siguiendo los estándares de seguridad."

---
*Este estándar es de cumplimiento obligatorio según el Nivel 1 de la Constitución.*
