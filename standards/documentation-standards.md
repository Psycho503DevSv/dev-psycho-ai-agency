# ESTÁNDARES DE DOCUMENTACIÓN (DOCUMENTATION STANDARDS)

## 1. EL MANIFIESTO DE LA DOCUMENTACIÓN
En AI DevOS, si no está documentado, no existe. La documentación es un producto vivo que evoluciona con el código.

## 2. ARCHIVOS OBLIGATORIOS POR PROYECTO
Todo proyecto nacido en este sistema debe contener:
1. **README.md:** Vista general, instalación, ejecución y arquitectura (en español).
2. **CHANGELOG.md:** Registro cronológico de cambios (siguiendo *Keep a Changelog*).
3. **ARCHITECTURE.md:** Diagramas de componentes y flujos de datos.
4. **API.md:** Documentación de endpoints o interfaces públicas.
5. **SECURITY.md:** Reportes de auditoría y gestión de riesgos.

## 3. FORMATO Y ESTRUCTURA DE DOCUMENTOS
- **Markdown Extendido:** Uso de Mermaid para diagramas, Katex para fórmulas y bloques de código con resaltado de sintaxis.
- **Jerarquía Clara:** Títulos `H1` para el nombre del documento, `H2` para secciones principales.
- **Links Relativos:** Siempre utilizar links markdown `[Texto](ruta/archivo.md)` para navegar entre documentos.

## 4. ACTUALIZACIÓN AUTOMÁTICA
- Después de cada cambio significativo en el código, el **Documentation Agent** debe sincronizar los archivos markdown.
- No se aceptan Pull Requests sin la actualización correspondiente de los docs.

## 5. REGLAS DE REDACCIÓN EN ESPAÑOL
- **Voz Activa:** "El sistema valida..." en lugar de "Es validado por el sistema...".
- **Consistencia de Términos:** No usar "carpeta" en un párrafo y "directorio" en otro; elegir uno y mantenerlo.
- **Claridad para Humanos y Agentes:** Escribir pensando que el próximo lector puede ser un humano u otro agente de IA.

## 6. EJEMPLO DE REGISTRO DE CAMBIOS (CHANGELOG)
```markdown
## [1.0.1] - 2026-06-13
### Añadido
- Nueva política de idioma español obligatoria.
### Corregido
- Bug en el registro de agentes que duplicaba entradas.
```

---
*Este estándar asegura la mantenibilidad del sistema a largo plazo.*
