# CATÁLOGO DE MCPs (MCP CATALOG)

## 1. VISTA GENERAL
Este documento detalla todas las herramientas (MCPs) disponibles en el ecosistema AI DevOS, sus funciones y quién tiene permiso para usarlas.

## 2. MCPs NUCLEARES (CORE)

### 2.1 Filesystem
- **Descripción:** Permite la manipulación de archivos y directorios en el host local.
- **Herramientas incluidas:** `read_file`, `write_file`, `list_dir`, `search_files`.
- **Uso Recomendado:** Solo para archivos dentro de las carpetas del proyecto. Evitar tocar archivos de sistema o configuración global del SO.
- **Permisos:** Orchestrator (Full), Developer (Write), Discovery (Read).

### 2.2 Git
- **Descripción:** Interfaz para el control de versiones Git.
- **Herramientas incluidas:** `init`, `add`, `commit`, `branch`, `merge`, `log`.
- **Uso Recomendado:** Obligatorio para cada cambio funcional. Los mensajes de commit deben estar en español.
- **Permisos:** Git Manager, Frontend Engineer, Backend Engineer.

### 2.3 Fetch (Http)
- **Descripción:** Permite obtener contenido de URLs externas.
- **Uso Recomendado:** Para lectura de documentación oficial o descarga de librerías.
- **Seguridad:** No usar para enviar datos sensibles a servidores no autorizados.

## 3. MCPs DE COMUNIDAD (COMMUNITY)

### 3.1 Docker
- **Descripción:** Gestión de contenedores y servicios.
- **Uso Recomendado:** Creación de entornos de base de datos o microservicios locales para pruebas.

### 3.2 Figma
- **Descripción:** Extracción de specs de diseño y assets.
- **Uso Recomendado:** Exclusivo para el UI/UX Designer y Frontend Engineer.

## 4. MCPs DE PERSISTENCIA (MEMORY)

### 4.1 Memory Layer (Custom)
- **Descripción:** Interfaz especializada para leer y escribir en la carpeta `/memory`.
- **Funciones:** Recuperar lecciones aprendidas anteriores para no repetir errores.

---
*Para registrar un nuevo MCP, consulte el documento 'mcp-governance.md'.*
