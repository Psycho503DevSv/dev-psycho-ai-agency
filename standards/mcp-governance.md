# GOBERNANZA MCP (MCP GOVERNANCE)

## 1. DEFINICIÓN Y ALCANCE
El sistema utiliza el Model Context Protocol (MCP) para conectar el cerebro (LLM) con el mundo real. Este documento regula el registro, uso y permisos de estos conectores.

## 2. CATEGORIZACIÓN DE MCPs
- **CORE:** Herramientas nucleares (Filesystem, Terminal, Memory, Git, Fetch). Ubicados en `/mcps/core`.
- **COMMUNITY:** Herramientas externas validadas (Docker, Figma, PostgreSQL). Ubicados en `/mcps/community`.
- **CUSTOM:** Desarrollos propios para necesidades específicas. Ubicados en `/mcps/custom`.

## 3. PROCESO DE REGISTRO
Ninguna herramienta puede ser invocada si no está en:
1. `registry/mcp-registry.json`: Configuración técnica.
2. `docs/mcp-catalog.md`: Descripción funcional y guía de uso.

### 3.1 Requisitos para el registro:
- Documento de seguridad de la herramienta.
- Definición clara de sus métodos y parámetros.
- Validación de que no causa efectos secundarios inesperados en el sistema de archivos raíz.

## 4. MATRIZ DE CAPACIDADES Y PERMISOS
Los permisos son granulares y por agente.
- **Solo Lectura:** El Agente Discovery solo tiene permiso `read_file` en el MCP Filesystem.
- **Escritura Controlada:** El Agente Developer puede escribir en `/projects` pero no en `/standards`.
- **Acceso Total:** Reservado exclusivamente para el Orchestrator.

## 5. SEGURIDAD Y CUMPLIMIENTO
- **Sanitización automática:** Todos los parámetros enviados a un MCP deben ser validados por el Orquestador.
- **Logging:** Cada llamada a un MCP debe quedar registrada en el log de sesión para auditoría.

## 6. MEJORES PRÁCTICAS
- **Cierre de Conexiones:** Los MCPs que abran sockets o bases de datos deben liberar recursos al terminar.
- **Manejo de Timeouts:** Ninguna operación de MCP debe bloquear al agente por más de 30 segundos sin feedback.

---
*Este documento es esencial para prevenir que un agente actúe fuera de sus límites técnicos.*
