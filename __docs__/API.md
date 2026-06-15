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

---
*Actualizado por: MCP-Architect | Fecha: 2026-06-15*
