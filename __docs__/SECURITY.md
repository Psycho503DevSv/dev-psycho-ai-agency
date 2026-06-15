# Estándares de Seguridad y Aislamiento

Este documento detalla las directivas de seguridad implementadas en el sistema para prevenir la ejecución no controlada y riesgos en la máquina del host.

## 1. Límites del Workspace del Filesystem (Sandbox de Rutas)

El despachador de herramientas local `McpExecutor` valida cada ruta de archivo que el agente intenta leer o escribir utilizando la función `_resolve_path`.

```python
def _resolve_path(self, path: str) -> str:
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.join(self.base_dir, path))
    else:
        path = os.path.abspath(path)
        
    if not path.startswith(os.path.abspath(self.base_dir)):
        raise PermissionError(f"Acceso denegado fuera del workspace: {path}")
    return path
```

### Reglas Clave:
* **Prevención de Path Traversal:** Cualquier intento del agente de usar `../` para salirse de la carpeta base del proyecto lanzará una excepción de seguridad `PermissionError`.
* **Retorno Controlado:** Las excepciones de seguridad son capturadas por el despachador de herramientas local y devueltas al agente como fallos de ejecución, impidiendo el acceso a archivos del sistema operativo host.

## 2. Aislamiento de Ejecución de Terminal

El comando ejecutado por la herramienta `run_command` corre en un subproceso local (`subprocess.run`).

### Salvaguardas Implementadas:
* **Timeout Estricto:** Cada comando tiene un tiempo de espera límite máximo de **60 segundos** (`timeout=60`). Si un proceso entra en un ciclo infinito o requiere interacción humana indefinida, se termina automáticamente previniendo el consumo indefinido de recursos de CPU.
* **Directorio de Trabajo Acotado (`cwd`):** El directorio de ejecución se valida previamente mediante `_resolve_path` para garantizar que los comandos solo puedan correr en el entorno de desarrollo autorizado.

## 3. Protección de API Keys y Credenciales

* Las claves de inferencia (`NVIDIA_API_KEY`, `OPENAI_API_KEY`) se cargan en memoria solo a través de variables de entorno administradas en el archivo `.env`.
* Nunca se suben claves ni credenciales a repositorios de control de código git (el archivo `.env` está explícitamente añadido a `.gitignore`).

---
*Actualizado por: Security Agent | Fecha: 2026-06-15*
