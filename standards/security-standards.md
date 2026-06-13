# ESTÁNDARES DE SEGURIDAD (SECURITY STANDARDS)

## 1. INTRODUCCIÓN
La seguridad en AI DevOS no es una opción, es una capa transversal a todo el desarrollo. Este documento define las reglas para proteger los datos, el código y el acceso al sistema.

## 2. REGLAS DE ORO DE SEGURIDAD
1. **Mínimo Privilegio:** Ningún agente o MCP tendrá más permisos de los estrictamente necesarios para su función.
2. **Defensa en Profundidad:** Múltiples capas de validación (agente, esquema, sistema).
3. **No Datos Sensibles en Git:** Prohibido subir API Keys, contraseñas o datos personales al repositorio.
4. **Validación de Entrada:** Toda información externa (Fetch) debe ser tratada como no confiable hasta ser saneada.

## 3. GESTIÓN DE SECRETOS
- **Uso de Variables de Entorno:** Todos los secretos deben residir en archivos `.env` o gestores de secretos.
- **Plantillas:** Solo se permiten en el repositorio archivos `.env.example`.
- **Rotación:** Todo agente de seguridad debe recomendar la rotación de credenciales cada vez que se detecte una posible exposición.

## 4. AUDITORÍA Y REVISIÓN
- **Revisión Obligatoria:** Antes de marcar un módulo de código como "Completado", el Security Engineer debe realizar un escaneo de vulnerabilidades.
- **OWASP:** Se deben seguir las guías de OWASP para el desarrollo de APIs y aplicaciones Web.
- **Validación de MCPs:** Solo los MCPs con checksum validado o de fuentes oficiales en `/mcps/core` se consideran seguros por defecto.

## 5. REGLAS PARA AGENTES
- **Prohibición de Ejecución Remota:** Ningún agente puede ejecutar scripts descargados de internet sin revisión previa en el sandbox.
- **Sanitización de Consultas SQL:** Es obligatorio el uso de consultas preparadas para evitar inyecciones.

## 6. SANITIZACIÓN DE PROMPTS Y SALIDAS (LLM SECURITY)
1. **Prevención de Inyección de Prompt:** No se debe pasar contenido directo del usuario a instrucciones de sistema sin envoltorios de seguridad.
2. **Filtro de Salida:** Los agentes deben revisar que sus respuestas no contengan secretos (Keys, Passwords) detectados mediante regex antes de enviarlas al usuario.
3. **Validación de Código Generado:** Todo código generado por la IA debe ser tratado como "no confiable" hasta ser parseado y validado sintácticamente.

## 7. CASOS DE USO Y PRÁCTICAS RECOMENDADAS
- **Ejemplo Práctico:** El Backend Engineer necesita conectar con Supabase. En lugar de escribir la KEY en el código, crea un acceso vía `process.env.SUPABASE_KEY` y registra en el `SECURITY.md` que la variable ha sido implementada.
- **Detección de Riesgos:** Si el Discovery Agent detecta que el usuario pide un sistema de pagos, debe activar automáticamente una bandera de "Cumplimiento PCI-DSS" en el plan de arquitectura.

---
*Jerarquía de Decisión: Nivel 2. Prevalece sobre estándares de codificación y arquitectura.*
