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

    def _log_security_violation(self, reason: str, details: str):
        """Registra incidentes de seguridad en el archivo de auditoría centralizado."""
        import datetime
        try:
            memory_dir = os.path.join(self.base_dir, "memory")
            os.makedirs(memory_dir, exist_ok=True)
            log_path = os.path.join(memory_dir, "security_audit.log")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [ALERTA DE SEGURIDAD] Motivo: {reason} | Detalles: {details}\n"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
            logger.warning(f"Incidente de seguridad registrado: {reason} - {details}")
        except Exception as e:
            logger.error(f"Error escribiendo en security_audit.log: {str(e)}")

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
        
        # Filtro de seguridad: Bloquear claves privadas, archivos del sistema/shell, e inyecciones en el entorno
        filename = os.path.basename(path).lower()
        forbidden_extensions = {".pem", ".key", ".pub", ".cer", ".crt", ".der", ".pfx", ".p12"}
        forbidden_files = {".bashrc", ".bash_profile", ".profile", ".zshrc", ".zprofile", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "authorized_keys"}
        
        # Comprobación de extensiones y nombres bloqueados
        _, ext = os.path.splitext(filename)
        if ext in forbidden_extensions or filename in forbidden_files or any(part.startswith(".ssh") for part in path.replace("\\", "/").split("/")):
            self._log_security_violation("Escritura bloqueada", f"Intento de escribir en archivo restringido: {path}")
            return {"status": "FAIL", "error": "Acceso denegado: No está permitido escribir claves privadas, credenciales ni configuraciones críticas de terminal."}

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

        # Filtro de Command Guardrails
        cmd_lower = command.lower()
        
        # Patrones destructivos o muy peligrosos
        dangerous_patterns = [
            r"\brm\s+-rf\b",        # rm -rf
            r"\brmdir\s+/s\b",      # rmdir /s
            r"\bdel\s+/s\b",        # del /s
            r"\bdel\s+/q\b",        # del /q
            r"\bformat\b",          # format disk
            r"\bmkfs\b",            # mkfs
            r"\bshutdown\b",        # shutdown
            r"\breboot\b",          # reboot
            r"\bpoweroff\b",        # poweroff
            r"\binit\s+0\b",        # init 0
            r":\(\)\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", # Fork bomb
            r">\s*/dev/sda\b",      # Raw write to sda
            r">\s*/dev/nvme",       # Raw write to nvme
            r"\|\s*sh\b",           # Piping to shell (curl ... | sh)
            r"\|\s*bash\b",         # Piping to bash
            r"\|\s*iex\b",          # Piping to Invoke-Expression (PowerShell)
            r"\binvoke-expression\b" # raw Invoke-Expression
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, cmd_lower):
                self._log_security_violation("Comando bloqueado", f"Comando detectado como peligroso: {command}")
                return {
                    "status": "FAIL",
                    "error": "Acceso denegado: Comando bloqueado por políticas de seguridad del sistema."
                }

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

    # --- Herramientas de Previsualización Nativa ---

    def _tool_preview_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Lanza la previsualización nativa del proyecto según su tipo."""
        project_type = args.get("project_type", "").strip().lower()
        project_path = args.get("project_path", ".")
        port = args.get("port", None)

        SUPPORTED_TYPES = {
            "web-estatica", "kinetic-typography",
            "web-framework", "android-apk", "chrome-extension"
        }

        if not project_type:
            return {"status": "FAIL", "error": "Se requiere el argumento 'project_type'."}

        if project_type not in SUPPORTED_TYPES:
            return {
                "status": "FAIL",
                "error": f"Tipo de proyecto '{project_type}' no soportado. Usa: {', '.join(sorted(SUPPORTED_TYPES))}"
            }

        logger.info(f"Iniciando previsualización para tipo: {project_type}")

        # --- Web estática y Tipografía Cinética ---
        if project_type in ("web-estatica", "kinetic-typography"):
            resolved_port = port or 8080
            resolved_path = self._resolve_path(project_path)

            # Lanzar servidor HTTP Python en background
            subprocess.Popen(
                ["python", "-m", "http.server", str(resolved_port)],
                cwd=resolved_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Abrir navegador automáticamente (Windows)
            url = f"http://localhost:{resolved_port}"
            subprocess.Popen(f"start {url}", shell=True)
            return {
                "status": "SUCCESS",
                "message": f"Servidor de previsualización iniciado en {url}",
                "url": url,
                "project_type": project_type
            }

        # --- Web con framework (React/Vue/Vite) ---
        if project_type == "web-framework":
            resolved_port = port or 5173
            resolved_path = self._resolve_path(project_path)

            subprocess.Popen(
                "npm run dev",
                cwd=resolved_path,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            url = f"http://localhost:{resolved_port}"
            # Esperar brevemente y luego abrir el browser
            import time
            time.sleep(3)
            subprocess.Popen(f"start {url}", shell=True)
            return {
                "status": "SUCCESS",
                "message": f"Servidor de desarrollo iniciado en {url}",
                "url": url,
                "project_type": project_type
            }

        # --- APK Android ---
        if project_type == "android-apk":
            apk_path = args.get("apk_path", "")
            package_name = args.get("package_name", "")

            if not apk_path or not package_name:
                return {
                    "status": "FAIL",
                    "error": "Para android-apk se requieren 'apk_path' y 'package_name' en los argumentos."
                }

            resolved_apk = self._resolve_path(apk_path)

            # Instalar/Reemplazar APK sin duplicar versiones (-r = replace)
            install_result = subprocess.run(
                f"adb install -r \"{resolved_apk}\"",
                shell=True, capture_output=True, text=True, timeout=60
            )
            if install_result.returncode != 0:
                return {
                    "status": "FAIL",
                    "error": "Fallo al instalar APK via ADB.",
                    "stderr": install_result.stderr
                }

            # Lanzar la app en el emulador/dispositivo
            launch_result = subprocess.run(
                f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1",
                shell=True, capture_output=True, text=True, timeout=30
            )
            return {
                "status": "SUCCESS" if launch_result.returncode == 0 else "FAIL",
                "message": f"APK instalada y lanzada: {package_name}",
                "install_output": install_result.stdout,
                "launch_output": launch_result.stdout,
                "project_type": project_type
            }

        # --- Extensión de Chrome ---
        if project_type == "chrome-extension":
            resolved_path = self._resolve_path(project_path)

            # Lanzar Chrome con la extensión cargada sin instalación
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                "google-chrome",
                "chromium"
            ]
            chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)

            if not chrome_exe:
                return {
                    "status": "FAIL",
                    "error": "No se encontró la instalación de Google Chrome. Instálalo y vuelve a intentar."
                }

            subprocess.Popen([
                chrome_exe,
                f"--load-extension={resolved_path}",
                "--no-first-run",
                "--new-window",
                "about:blank"
            ])
            return {
                "status": "SUCCESS",
                "message": f"Chrome lanzado con extensión cargada desde: {resolved_path}",
                "project_type": project_type
            }

        return {"status": "FAIL", "error": "Tipo no manejado."}

