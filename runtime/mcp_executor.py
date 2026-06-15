import os
import subprocess
import logging
from typing import Dict, Any

logger = logging.getLogger("McpExecutor")

class McpExecutor:
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Despacha y ejecuta herramientas simulando un servidor MCP local."""
        logger.info(f"Ejecutando herramienta MCP: {tool_name} con argumentos: {arguments}")
        
        try:
            method = getattr(self, f"_tool_{tool_name.replace(':', '_')}", None)
            if not method:
                return {"status": "FAIL", "error": f"Herramienta '{tool_name}' no soportada en el ejecutor local."}
            return method(arguments)
        except Exception as e:
            logger.exception(f"Error ejecutando herramienta {tool_name}")
            return {"status": "FAIL", "error": f"Excepción en herramienta: {str(e)}"}

    def _resolve_path(self, path: str) -> str:
        """Resuelve y valida que la ruta esté dentro del workspace base."""
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.base_dir, path))
        else:
            path = os.path.abspath(path)
            
        # Seguridad básica para evitar salirse del workspace
        if not path.startswith(os.path.abspath(self.base_dir)):
            raise PermissionError(f"Acceso denegado fuera del workspace: {path}")
        return path

    # --- Herramientas del Filesystem ---

    def _tool_read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(args.get("path", ""))
        if not os.path.exists(path):
            return {"status": "FAIL", "error": f"Archivo no encontrado: {path}"}
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return {"status": "SUCCESS", "content": content}

    def _tool_write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(args.get("path", ""))
        content = args.get("content", "")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "SUCCESS", "message": f"Archivo escrito exitosamente en {path}"}

    def _tool_list_dir(self, args: Dict[str, Any]) -> Dict[str, Any]:
        path = self._resolve_path(args.get("path", "."))
        if not os.path.exists(path) or not os.path.isdir(path):
            return {"status": "FAIL", "error": f"Directorio no encontrado: {path}"}
        
        items = []
        for entry in os.scandir(path):
            items.append({
                "name": entry.name,
                "is_directory": entry.is_dir(),
                "size": entry.stat().st_size if entry.is_file() else 0
            })
        return {"status": "SUCCESS", "items": items}

    # --- Herramientas de Comandos / Terminal ---

    def _tool_run_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        command = args.get("command", "")
        cwd = args.get("cwd", ".")
        resolved_cwd = self._resolve_path(cwd)

        if not command:
            return {"status": "FAIL", "error": "Comando vacío"}

        logger.info(f"Ejecutando comando en terminal autónomo: '{command}' en '{resolved_cwd}'")
        
        try:
            # Ejecutar con shell=True de forma segura
            result = subprocess.run(
                command,
                cwd=resolved_cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )
            return {
                "status": "SUCCESS" if result.returncode == 0 else "FAIL",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired as te:
            return {
                "status": "FAIL",
                "error": "El comando excedió el tiempo límite de ejecución de 60 segundos.",
                "stdout": te.stdout or "",
                "stderr": te.stderr or ""
            }
        except Exception as e:
            return {"status": "FAIL", "error": f"Fallo en ejecución: {str(e)}"}

    # --- Herramientas de Interacción Humana ---

    def _tool_ask_user(self, args: Dict[str, Any]) -> Dict[str, Any]:
        question = args.get("question", "")
        if not question:
            return {"status": "FAIL", "error": "La pregunta no puede estar vacía."}
            
        print("\n" + "="*50)
        print(f"💬 PREGUNTA DEL AGENTE:\n{question}")
        print("="*50)
        
        try:
            user_response = input("Respuesta > ")
            return {"status": "SUCCESS", "response": user_response}
        except Exception as e:
            return {"status": "FAIL", "error": f"Error leyendo respuesta del usuario: {str(e)}"}
