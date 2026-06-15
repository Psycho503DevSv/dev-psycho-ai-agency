# Especificaciones del API y Protocolos de Comunicación

Este documento detalla el protocolo de comunicación interno del loop del agente, llamadas a LLMs y las herramientas locales MCP.

## 1. Protocolo de Inferencia (Agent Loop Inferences)

El runtime realiza llamadas directas a las APIs utilizando HTTP y la librería `requests`.

### Endpoint de NVIDIA NIM (Prioritario si se define `NVIDIA_API_KEY`)
* **URL:** `https://integrate.api.nvidia.com/v1/chat/completions`
* **Modelo por Defecto:** `meta/llama-3.1-8b-instruct`
* **Headers:**
  ```json
  {
    "Authorization": "Bearer <NVIDIA_API_KEY>",
    "Content-Type": "application/json"
  }
  ```

### Endpoint de OpenAI (Alternativo si no hay clave NVIDIA)
* **URL:** `https://api.openai.com/v1/chat/completions`
* **Modelo por Defecto:** `gpt-4o-mini`
* **Headers:**
  ```json
  {
    "Authorization": "Bearer <OPENAI_API_KEY>",
    "Content-Type": "application/json"
  }
  ```

## 2. Protocolo de LLM Agent Loop (Llamada a Herramientas)

Los agentes deben estructurar sus respuestas incluyendo bloques JSON de llamadas a herramientas cuando deseen ejecutar una acción local. El runner detecta bloques JSON con la siguiente estructura:

```json
{
  "tool": "run_command",
  "arguments": {
    "command": "pytest",
    "cwd": "."
  }
}
```

El runner captura el bloque JSON, lo valida, lo ejecuta a través de `McpExecutor`, y devuelve el resultado al agente en el siguiente turno de la conversación de LLM:

```json
{
  "status": "SUCCESS",
  "return_code": 0,
  "stdout": "... salida del comando ...",
  "stderr": ""
}
```

### 2.1 Robustez del Agent Loop (v1.2.0+)

El runtime aplica las siguientes salvaguardas automáticas en cada turno del agente:

| Salvaguarda | Comportamiento |
| :--- | :--- |
| **Reintentos de LLM** | La llamada al LLM se reintenta hasta 3 veces con backoff exponencial (2s → 4s → 8s) ante errores de red o rate-limits. |
| **Parser Auto-Correctivo** | `_parse_tool_call` detecta JSON en bloques ` ```json `, ` ``` ` sin etiqueta o JSON crudo. Aplica 4 correcciones automáticas de errores sintácticos comunes de LLMs. |
| **Corrección de JSON Inválido** | Si el agente intenta llamar a una herramienta con JSON malformado, el runner le devuelve un mensaje de error descriptivo para que lo reformatee, sin romper el bucle. |
| **Anti-repetición de respuestas** | Si el agente emite dos respuestas consecutivas idénticas, el bucle se corta inmediatamente. |
| **Anti-repetición de herramientas** | Si el agente llama a la misma herramienta con los mismos argumentos 3+ veces, el bucle se aborta con log de error crítico para evitar consumo infinito de tokens. |

## 3. Catálogo de Herramientas MCP Locales

El módulo `runtime/mcp_executor.py` implementa el soporte local nativo para las siguientes herramientas:

### `read_file`
Lee el contenido de un archivo local.
* **Argumentos:** `{"path": "ruta/al/archivo.ext"}`
* **Retorno:** `{"status": "SUCCESS", "content": "... contenido ..."}` o `{"status": "FAIL", "error": "motivo"}`

### `write_file`
Escribe contenido en un archivo (crea directorios padres automáticamente).
* **Argumentos:** `{"path": "ruta/al/archivo.ext", "content": "... contenido ..."}`
* **Retorno:** `{"status": "SUCCESS", "message": "mensaje de éxito"}`

### `list_dir`
Muestra el contenido de un directorio.
* **Argumentos:** `{"path": "ruta/al/directorio"}`
* **Retorno:** `{"status": "SUCCESS", "items": [{"name": "...", "is_directory": true/false, "size": 123}]}`

### `run_command`
Ejecuta un comando en la terminal local del sistema operativo de manera síncrona.
* **Argumentos:** `{"command": "comando a ejecutar", "cwd": "directorio de trabajo"}`
* **Retorno:** `{"status": "SUCCESS/FAIL", "return_code": int, "stdout": "...", "stderr": "..."}`
* **Límite de tiempo:** 60 segundos por comando.

### `ask_user`
Detiene la ejecución del agente temporalmente en consola para realizar una pregunta interactiva al usuario y esperar su respuesta.
* **Argumentos:** `{"question": "Texto de la pregunta"}`
* **Retorno:** `{"status": "SUCCESS", "response": "... respuesta escrita por el usuario ..."}`

### `preview_project`
Lanza la previsualización nativa del proyecto según su tipo (web-estatica, kinetic-typography, web-framework, android-apk, chrome-extension).
* **Argumentos:**
  * `project_type` (string, obligatorio): El tipo de proyecto (`web-estatica`, `web-framework`, `android-apk`, `chrome-extension`, `kinetic-typography`).
  * `project_path` (string, opcional): Ruta base del proyecto. Por defecto es `"."`.
  * `port` (int, opcional): Puerto para servidores locales HTTP o dev servers.
  * `apk_path` (string, opcional): Ruta del archivo APK (requerido para `android-apk`).
  * `package_name` (string, opcional): Nombre del paquete Android (requerido para `android-apk`).
* **Retorno:** `{"status": "SUCCESS/FAIL", "message": "mensaje descriptivo", "project_type": "...", ...}`

## 4. Políticas de Seguridad y Sandboxing (v1.3.0+)

El runtime aplica políticas activas para asegurar la ejecución del agente en entornos de desarrollo abiertos y autoentrenables:

### 4.1 Command Guardrails (run_command)
Se interceptan comandos peligrosos antes de su ejecución. Comandos que contengan patrones destructivos o de alteración del sistema son rechazados inmediatamente retornando `FAIL` con error de acceso denegado.
* **Patrones Bloqueados:** `rm -rf`, `rmdir /s`, `del /s`, `del /q`, `format`, `mkfs`, `shutdown`, `reboot`, `poweroff`, `init 0`, Fork bombs (`:(){ :|:& };:`), redirecciones crudas de disco (`> /dev/sda`), y tuberías a intérpretes de comandos sin verificar (`| sh`, `| bash`, `| iex`, `Invoke-Expression`).

### 4.2 Filtro de Escritura del Filesystem (write_file)
Evita la sobreescritura de credenciales, llaves de seguridad y configuraciones de sesión crítica de la máquina anfitriona.
* **Extensiones Denegadas:** `.pem`, `.key`, `.pub`, `.cer`, `.crt`, `.der`, `.pfx`, `.p12`
* **Nombres de Archivos Bloqueados:** `.bashrc`, `.bash_profile`, `.profile`, `.zshrc`, `.zprofile`, `id_rsa`, `id_dsa`, `id_ecdsa`, `id_ed25519`, `authorized_keys`.
* **Rutas Bloqueadas:** Cualquier ruta que contenga subcarpetas `.ssh/` o intente saltar los límites del workspace base.

### 4.3 Sanitización de Contexto contra Prompt Injection (agent_loader)
Sanitiza de forma proactiva la memoria dinámica del proyecto cargada desde Graphiti u otros archivos markdown, reemplazando instrucciones de inyección típicas (ej. `"ignore previous instructions"`, `"disregard all previous"`, `"you are now a..."`, `"nueva directiva:"`) por marcadores de advertencia (`[INJECTION_DETECTOR: ...]`), protegiendo al agente del secuestro de comportamiento por parte de código ajeno o descripciones de tareas manipuladas.

### 4.4 Registro de Auditoría
Cualquier intento de violación a estas reglas de seguridad queda registrado inmediatamente en `memory/security_audit.log` con marca de tiempo y descripción del recurso o comando bloqueado.

---
*Actualizado por: Security & Sandboxing Agent | Fecha: 2026-06-15*
