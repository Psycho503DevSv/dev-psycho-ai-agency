# ESTÁNDARES DE DOCUMENTACIÓN (DOCUMENTATION STANDARDS)

## 1. EL MANIFIESTO DE LA DOCUMENTACIÓN
En AI DevOS, si no está documentado, no existe. La documentación es un producto vivo que evoluciona con el código.

## 2. CARPETA `__docs__` — OBLIGATORIA EN TODO PROYECTO
Todo proyecto creado en este sistema debe tener una carpeta `__docs__/` en su raíz con los siguientes archivos:

| Archivo | Propósito |
|---|---|
| `README.md` (raíz) | Vista general, instalación, ejecución, arquitectura. Siempre en la raíz del proyecto. |
| `__docs__/ARCHITECTURE.md` | Diagramas de componentes, flujos de datos y decisiones arquitectónicas. |
| `__docs__/API.md` | Documentación de endpoints, interfaces y contratos públicos. |
| `__docs__/DATABASE.md` | **Scripts SQL listos para ejecutar:** creación de tablas, migraciones, índices y seeds. Auditoria completa del schema. |
| `__docs__/CHANGELOG.md` | Registro cronológico de cambios (formato *Keep a Changelog*). |
| `__docs__/SECURITY.md` | Reportes de auditoría, riesgos detectados y medidas aplicadas. |
| `__docs__/SETUP.md` | Guía completa de instalación de dependencias y configuración del entorno. |

## 3. REGLA DE ORO: ACTUALIZACIÓN OBLIGATORIA DESPUÉS DE CADA CAMBIO
**Todo agente que modifique código tiene la obligación inmediata de:**
1. Leer el documento `__docs__/` correspondiente al módulo modificado.
2. Editar y actualizar su contenido reflejando el cambio realizado.
3. Actualizar el `README.md` en la raíz si el cambio afecta la interfaz, instalación o arquitectura visible del proyecto.
4. Registrar la entrada en `__docs__/CHANGELOG.md`.

> ⛔ Ningún cambio de código se considera completo si no va acompañado de la actualización documental.

## 4. EJECUCIÓN AUTÓNOMA VÍA MCP (TERMINAL)
Los agentes no deben pedir al usuario que ejecute comandos manualmente.
- **Obligación:** Toda instalación de dependencias, limpieza de caché, ejecución de builds o scripts de setup debe ser propuesta y ejecutada por el agente a través de las herramientas de terminal MCP.
- **Rol del Usuario:** Únicamente aprobar o rechazar la ejecución del comando (responder "simon" o "no").
- **Verificación:** El agente debe confirmar mediante la salida del terminal que el comando se ejecutó exitosamente antes de continuar.

## 5. FORMATO Y ESTRUCTURA DE DOCUMENTOS
- **Markdown Extendido:** Uso de Mermaid para diagramas, tablas y bloques de código con resaltado de sintaxis.
- **Jerarquía Clara:** `H1` para el nombre del documento, `H2` para secciones principales, `H3` para subsecciones.
- **Links Relativos:** Usar links markdown `[Texto](ruta/archivo.md)` para navegar entre documentos.
- **Idioma:** Todo documento técnico debe redactarse en **español**, salvo identificadores de código.

## 6. EJEMPLO DE ENTRADA EN CHANGELOG
```markdown
## [1.2.0] - 2026-06-14
### Añadido
- Módulo `auto_learner.py` para autoentrenamiento continuo post-workflow.
### Modificado
- `workflow_runner.py` integra el hook de autoaprendizaje al final de cada ejecución.
### Eliminado
- Carpeta `devtasks/` removida del repositorio raíz.
```

---
*Jerarquía de Decisión: Nivel 1 (Constitución). Este estándar asegura la mantenibilidad del sistema a largo plazo.*
