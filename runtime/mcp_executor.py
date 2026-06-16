import os
import re
import sys
import subprocess
from typing import Dict, Any, Optional

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError in console
if sys.platform == "win32" and "pytest" not in sys.modules:
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass

from runtime.logger import logger
from runtime.schemas import CommandSchema, ExecutionResultSchema

# ── Docker sandbox detection ──────────────────────────────────────────────────
# Cuando AGENT_ENV=docker el proceso ya corre dentro del contenedor.
# Cuando corre local y USE_DOCKER_SANDBOX=true intentamos usar `docker exec`
# para aislar comandos de terminal en el contenedor del agente.
_AGENT_ENV        = os.environ.get("AGENT_ENV", "local")
_USE_DOCKER_SB    = os.environ.get("USE_DOCKER_SANDBOX", "false").lower() == "true"
_DOCKER_CONTAINER = os.environ.get("AGENT_CONTAINER_NAME", "psycho503_agent")

class McpExecutor:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.active_project_name: Optional[str] = None
        self.active_workflow_id: Optional[str] = None


    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], agent_role: Optional[str] = None) -> Dict[str, Any]:
        """Despacha y ejecuta herramientas simulando un servidor MCP local, verificando permisos por rol."""
        logger.info(f"Ejecutando herramienta MCP: {tool_name} para rol '{agent_role}' con argumentos: {arguments}")
        
        # Guardrail granular por fase/workflow
        if self.active_workflow_id:
            if self.active_workflow_id == "wf-discovery":
                allowed_discovery_tools = {"read_file", "write_file", "list_dir", "ask_user"}
                if tool_name not in allowed_discovery_tools:
                    return {
                        "status": "FAIL",
                        "error": f"Acceso Denegado: La herramienta '{tool_name}' no está permitida en la fase de descubrimiento ({self.active_workflow_id})."
                    }
            elif self.active_workflow_id == "wf-planning":
                allowed_planning_tools = {"read_file", "write_file", "list_dir", "ask_user", "search_code"}
                if tool_name not in allowed_planning_tools:
                    return {
                        "status": "FAIL",
                        "error": f"Acceso Denegado: La herramienta '{tool_name}' no está permitida en la fase de planificación ({self.active_workflow_id})."
                    }

        # Guardrail granular por rol para la herramienta 'run_command'
        if tool_name == "run_command" and agent_role:
            cmd = arguments.get("command", "").strip()
            if not self._check_role_permissions(agent_role, cmd):
                return {
                    "status": "FAIL",
                    "error": f"Acceso Denegado: El rol '{agent_role}' no tiene permiso para ejecutar el comando: {cmd}"
                }

        try:
            method = getattr(self, f"_tool_{tool_name.replace(':', '_')}", None)
            if not method:
                res = {"status": "FAIL", "error": f"Herramienta '{tool_name}' no soportada en el ejecutor local."}
            else:
                res = method(arguments)

                
            # Loguear evento de herramienta al dashboard
            try:
                from runtime.dashboard import update_dashboard_state
                update_dashboard_state({"recent_tool_calls": {"tool": tool_name, "args": arguments, "status": res.get("status", "SUCCESS")}})
            except ImportError:
                try:
                    from dashboard import update_dashboard_state
                    update_dashboard_state({"recent_tool_calls": {"tool": tool_name, "args": arguments, "status": res.get("status", "SUCCESS")}})
                except Exception:
                    pass
            return res
        except Exception as e:
            logger.exception(f"Error ejecutando herramienta {tool_name}")
            res = {"status": "FAIL", "error": f"Excepción en herramienta: {str(e)}"}
            try:
                from runtime.dashboard import update_dashboard_state
                update_dashboard_state({"recent_tool_calls": {"tool": tool_name, "args": arguments, "status": "FAIL"}})
            except Exception:
                pass
            return res

    def _resolve_path(self, path: str) -> str:
        """Resuelve y valida que la ruta esté dentro del workspace base, aislando la memoria por proyecto."""
        if not os.path.isabs(path):
            resolved_path = os.path.abspath(os.path.join(self.base_dir, path))
        else:
            resolved_path = os.path.abspath(path)
            
        # Seguridad básica para evitar salirse del workspace
        if not resolved_path.startswith(os.path.abspath(self.base_dir)):
            raise PermissionError(f"Acceso denegado fuera del workspace: {resolved_path}")
            
        # Aislamiento de archivos de memoria por proyecto
        memory_dir_abs = os.path.abspath(os.path.join(self.base_dir, "memory"))
        if self.active_project_name and resolved_path.startswith(memory_dir_abs):
            filename = os.path.basename(resolved_path)
            relative_subpath = os.path.relpath(resolved_path, memory_dir_abs)
            is_already_project_scoped = relative_subpath.replace("\\", "/").startswith("projects/")
            # Excepciones globales que no se aíslan por proyecto
            is_global = filename in ["lessons_learned.md", "token_usage.json", "security_audit.log"] or is_already_project_scoped
            
            if not is_global:
                resolved_path = os.path.abspath(os.path.join(memory_dir_abs, "projects", self.active_project_name, relative_subpath))
                
        return resolved_path

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
            
            # Enviar alerta en vivo al dashboard
            try:
                from runtime.dashboard import add_security_alert
                add_security_alert(f"[{timestamp}] ALERTA: {reason} - {details}")
            except ImportError:
                try:
                    from dashboard import add_security_alert
                    add_security_alert(f"[{timestamp}] ALERTA: {reason} - {details}")
                except Exception:
                    pass
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
        
        filename = os.path.basename(path).lower()
        forbidden_extensions = {".pem", ".key", ".pub", ".cer", ".crt", ".der", ".pfx", ".p12"}
        forbidden_files = {".bashrc", ".bash_profile", ".profile", ".zshrc", ".zprofile", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", "authorized_keys"}
        
        # Comprobación de extensiones y nombres bloqueados
        _, ext = os.path.splitext(filename)
        if ext in forbidden_extensions or filename in forbidden_files or any(part.startswith(".ssh") for part in path.replace("\\", "/").split("/")):
            self._log_security_violation("Escritura bloqueada", f"Intento de escribir en archivo restringido: {path}")
            return {"status": "FAIL", "error": "Acceso denegado: No está permitido escribir claves privadas, credenciales ni configuraciones críticas de terminal."}

        # 1. Protección contra sobrescritura destructiva/truncada de memoria
        is_requirements = filename == "requirements.md"
        is_architecture = filename == "architecture.md"
        if (is_requirements or is_architecture) and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    old_content = f.read()
                if len(old_content) > 0:
                    pct_reduction = (len(old_content) - len(content)) / len(old_content)
                    if pct_reduction > 0.30:
                        return {
                            "status": "FAIL",
                            "error": f"Acceso Denegado: Intento de sobrescritura destructiva detectado. La reducción de contenido del archivo es del {pct_reduction:.1%}. Debes preservar la información previamente validada."
                        }
                    if is_requirements and "Entrevista validada" in old_content and "Entrevista validada" not in content:
                        return {
                            "status": "FAIL",
                            "error": "Acceso Denegado: No puedes eliminar la marca de validación 'Entrevista validada' del archivo de requisitos."
                        }
                    if is_architecture and "##" in old_content and "##" not in content:
                        return {
                            "status": "FAIL",
                            "error": "Acceso Denegado: No puedes eliminar las secciones estructuradas de arquitectura previamente definidas."
                        }
            except Exception as e:
                logger.warning(f"Error en protección de sobreescritura: {e}")

        # 2. Bloquear secretos en el repositorio (excepto plantillas .env.example)
        if filename != ".env.example":
            secret_patterns = [
                r"api_key\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                r"token\s*=\s*['\"][0-9]+:[a-zA-Z0-9_-]{35,}['\"]",
                r"password\s*=\s*['\"][a-zA-Z0-9_-]{8,}['\"]",
                r"gemini_api_key\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]",
                r"groq_api_key\s*=\s*['\"][a-zA-Z0-9_-]{20,}['\"]"
            ]
            import re
            for pat in secret_patterns:
                if re.search(pat, content, re.IGNORECASE):
                    self._log_security_violation("Secretos detectados", f"Intento de escribir secretos directamente en el código de {path}")
                    return {
                        "status": "FAIL",
                        "error": "Acceso Denegado: No está permitido guardar secretos o API keys directamente en los archivos de código del repositorio. Utiliza variables de entorno o plantillas .env.example."
                    }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "SUCCESS", "message": f"Archivo escrito exitosamente en {path}"}

    def _tool_search_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una búsqueda RAG rápida de código o archivos en el workspace."""
        query = args.get("query", "")
        if not query:
            return {"status": "FAIL", "error": "Argumento 'query' es obligatorio."}
            
        try:
            # Importación dinámica para evitar acoplamientos circulares
            try:
                from runtime.rag_engine import RAGEngine
            except ImportError:
                from rag_engine import RAGEngine
                
            engine = RAGEngine(self.base_dir)
            results = engine.search(query)
            return {"status": "SUCCESS", "results": results}
        except Exception as e:
            return {"status": "FAIL", "error": f"Error buscando en el índice de código: {str(e)}"}

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

    # ── Guardrails compartidos ────────────────────────────────────────────────
    _DANGEROUS_PATTERNS = [
        r"\brm\s+-rf\b",                                    # rm -rf
        r"\brmdir\s+/s\b",                                  # rmdir /s
        r"\bdel\s+/s\b",                                    # del /s
        r"\bdel\s+/q\b",                                    # del /q
        r"\bformat\b",                                      # format disk
        r"\bmkfs\b",                                        # mkfs
        r"\bshutdown\b",                                    # shutdown
        r"\breboot\b",                                      # reboot
        r"\bpoweroff\b",                                    # poweroff
        r"\binit\s+0\b",                                    # init 0
        r":\(\)\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",          # Fork bomb
        r">\s*/dev/sda\b",                                  # Raw write to sda
        r">\s*/dev/nvme",                                   # Raw write to nvme
        r"\|\s*sh\b",                                       # Piping to shell
        r"\|\s*bash\b",                                     # Piping to bash
        r"\|\s*iex\b",                                      # PowerShell IEX
        r"\binvoke-expression\b",                           # raw IEX
    ]

    # Whitelist granular de comandos por rol de agente (10/10 Seguridad)
    _ROLE_COMMAND_WHITELIST = {
        "frontend-developer": [
            r"\bnpm\b", r"\bnpx\b", r"\bnode\b", r"\bgit\b", r"\becho\b"
        ],
        "backend-developer": [
            r"\bnpm\b", r"\bnpx\b", r"\bnode\b", r"\bpython\b", r"\bpip\b", r"\bgit\b", r"\becho\b"
        ],
        "qa-engineer": [
            r"\bnpm\b", r"\bpytest\b", r"\bpython\b", r"\bgit\b", r"\becho\b"
        ],
        "security-analyst": [
            r"\bnpm\b", r"\baudit\b", r"\bsafety\b", r"\bbandit\b", r"\bgit\b"
        ],
        "project-manager": [
            r"\bgit\b", r"\becho\b", r"\bcat\b"
        ],
        "ceo": [
            r".*" # El CEO tiene control total
        ]
    }

    def _check_role_permissions(self, role: str, command: str) -> bool:
        """Comprueba si el rol del agente tiene autorización para ejecutar el comando dado."""
        role_clean = role.lower().strip()
        cmd_lower = command.lower().strip()
        
        # Si el rol no está definido, por defecto somos permisivos pero con advertencia
        if role_clean not in self._ROLE_COMMAND_WHITELIST:
            logger.warning(f"Rol '{role_clean}' no catalogado en whitelist. Permitiendo por compatibilidad.")
            return True

        allowed_patterns = self._ROLE_COMMAND_WHITELIST[role_clean]
        for pattern in allowed_patterns:
            if re.search(pattern, cmd_lower):
                return True

        self._log_security_violation(
            "Violación de permisos de Rol",
            f"El rol '{role}' intentó ejecutar un comando denegado: {command}"
        )
        return False


    def _check_guardrails(self, command: str) -> bool:
        """Retorna True si el comando pasa los guardrails (es seguro)."""
        cmd_lower = command.lower()
        for pattern in self._DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                self._log_security_violation(
                    "Comando bloqueado",
                    f"Comando detectado como peligroso: {command}"
                )
                return False
        return True

    def _run_in_docker_sandbox(self, command: str, cwd: str, timeout: int = 60) -> Dict[str, Any]:
        """Ejecuta `command` dentro del contenedor Docker del agente via `docker exec`."""
        logger.info(f"[SANDBOX-DOCKER] Ejecutando en contenedor '{_DOCKER_CONTAINER}': {command}")
        docker_cmd = [
            "docker", "exec",
            "--workdir", "/workspace",
            _DOCKER_CONTAINER,
            "bash", "-c", command
        ]
        try:
            result = subprocess.run(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            return {
                "status": "SUCCESS" if result.returncode == 0 else "FAIL",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "sandbox": "docker"
            }
        except FileNotFoundError:
            return {
                "status": "FAIL",
                "error": "Docker no encontrado. Instala Docker Desktop o activa el daemon.",
                "sandbox": "docker"
            }
        except subprocess.TimeoutExpired as te:
            return {
                "status": "FAIL",
                "error": "Timeout en sandbox Docker (60s).",
                "stdout": te.stdout or "",
                "stderr": te.stderr or "",
                "sandbox": "docker"
            }

    def _tool_run_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Validación estricta del comando de entrada usando Pydantic
            validated_input = CommandSchema(command=args.get("command", ""))
            command = validated_input.command
        except Exception as ve:
            return {"status": "FAIL", "error": f"Entrada inválida: {str(ve)}"}

        cwd = args.get("cwd", ".")
        timeout = int(args.get("timeout", 60))

        # ── Guardrails de seguridad ────────────────────────────────────────── #
        if not self._check_guardrails(command):
            return {
                "status": "FAIL",
                "error": "Acceso denegado: Comando bloqueado por políticas de seguridad del sistema."
            }

        # ── Routing: Docker sandbox vs. local ─────────────────────────────── #
        # Caso 1: Corriendo en entorno local CON sandbox Docker habilitado
        if _AGENT_ENV == "local" and _USE_DOCKER_SB:
            logger.info(f"[SANDBOX] Redirigiendo comando al contenedor Docker '{_DOCKER_CONTAINER}'")
            raw_res = self._run_in_docker_sandbox(command, cwd, timeout)
            # Validar salida
            try:
                validated_output = ExecutionResultSchema(
                    status=raw_res.get("status", "FAIL"),
                    stdout=raw_res.get("stdout", ""),
                    stderr=raw_res.get("stderr", ""),
                    code=raw_res.get("return_code", -1),
                    sandbox="docker",
                    message=raw_res.get("error")
                )
                return validated_output.model_dump()
            except Exception as e:
                return {"status": "FAIL", "error": f"Error de validación de salida Docker: {str(e)}"}

        # Caso 2: Ya corremos dentro del contenedor Docker (auto-sandbox)
        if _AGENT_ENV == "docker":
            logger.info(f"[SANDBOX-DOCKER] El proceso ya está en el contenedor. Ejecutando localmente.")
            # El CWD dentro del contenedor es /workspace
            resolved_cwd = "/workspace"
        else:
            # Caso 3: Modo local puro, resolución de paths normal
            resolved_cwd = self._resolve_path(cwd)

        logger.info(f"Ejecutando comando: '{command}' en '{resolved_cwd}'")

        try:
            result = subprocess.run(
                command,
                cwd=resolved_cwd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            raw_res = {
                "status": "SUCCESS" if result.returncode == 0 else "FAIL",
                "code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "sandbox": _AGENT_ENV
            }
        except subprocess.TimeoutExpired as te:
            raw_res = {
                "status": "FAIL",
                "code": -1,
                "stdout": te.stdout or "",
                "stderr": te.stderr or "",
                "sandbox": _AGENT_ENV,
                "message": f"El comando excedió el tiempo límite de {timeout} segundos."
            }
        except Exception as e:
            raw_res = {
                "status": "FAIL",
                "code": -1,
                "stdout": "",
                "stderr": str(e),
                "sandbox": _AGENT_ENV,
                "message": f"Fallo en ejecución: {str(e)}"
            }

        # Validar el resultado de la ejecución con Pydantic antes de retornarlo
        try:
            validated_output = ExecutionResultSchema(
                status=str(raw_res["status"]),
                stdout=str(raw_res.get("stdout") or ""),
                stderr=str(raw_res.get("stderr") or ""),
                code=int(raw_res.get("code") if raw_res.get("code") is not None else -1),
                sandbox=str(raw_res.get("sandbox", "local")),
                message=str(raw_res.get("message")) if raw_res.get("message") is not None else None
            )
            return validated_output.model_dump()
        except Exception as ve:
            return {"status": "FAIL", "error": f"Error validando salida de ejecución: {str(ve)}"}


    # --- Herramientas de Interacción Humana ---

    def _tool_ask_user(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # Accept multiple possible arg names that LLMs tend to use
        question = (
            args.get("question") or
            args.get("prompt") or
            args.get("pregunta") or
            args.get("message") or
            args.get("text") or
            ""
        )
        if not question:
            return {"status": "FAIL", "error": "La pregunta no puede estar vacía."}

        import threading
        import sys as _sys
        from runtime.dashboard import (
            set_pending_question,
            clear_pending_question,
            wait_for_response,
            get_web_response,
            _question_event
        )

        preview_content = None
        if self.active_project_name and self.active_workflow_id:
            memory_dir = os.path.join(self.base_dir, "memory", "projects", self.active_project_name)
            if self.active_workflow_id == "wf-discovery":
                doc_path = os.path.join(memory_dir, "requirements.md")
                if os.path.exists(doc_path):
                    try:
                        with open(doc_path, "r", encoding="utf-8") as f:
                            preview_content = f.read()
                    except Exception:
                        pass
            elif self.active_workflow_id == "wf-planning":
                doc_path = os.path.join(memory_dir, "architecture.md")
                if os.path.exists(doc_path):
                    try:
                        with open(doc_path, "r", encoding="utf-8") as f:
                            preview_content = f.read()
                    except Exception:
                        pass

        set_pending_question(question, document_preview=preview_content)
        _question_event.clear()

        # Only try console input if we have an interactive TTY or we are running under pytest
        console_res = []
        is_tty = _sys.stdin is not None and hasattr(_sys.stdin, 'isatty') and _sys.stdin.isatty()
        is_pytest = "pytest" in _sys.modules

        if is_tty or is_pytest:
            print("\n" + "="*50)
            print(f"PREGUNTA DEL AGENTE:\n{question}")
            print("="*50)

            def read_console():
                try:
                    val = input("Respuesta (o responde via Web UI en http://localhost:8050) > ")
                    console_res.append(val)
                    _question_event.set()
                except Exception:
                    pass

            t = threading.Thread(target=read_console, daemon=True)
            t.start()

        # Wait up to 5 minutes for a response (console OR web dashboard)
        logger.info(f"[ask_user] Esperando respuesta humana via dashboard en http://localhost:8050 ...")
        wait_timeout = 2 if is_pytest else 300
        responded = _question_event.wait(timeout=wait_timeout)
        clear_pending_question()

        if not responded:
            return {"status": "FAIL", "error": f"Tiempo de espera agotado ({wait_timeout}s). No se recibió respuesta del usuario."}

        if console_res:
            return {"status": "SUCCESS", "response": console_res[0]}

        web_val = get_web_response()
        if web_val is not None:
            return {"status": "SUCCESS", "response": web_val}

        return {"status": "FAIL", "error": "No se recibio respuesta valida."}

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

    def cleanup(self):
        """Detiene y remueve el contenedor del sandbox de Docker ordenadamente si está en ejecución."""
        if _AGENT_ENV == "local" and _USE_DOCKER_SB:
            logger.info(f"[CLEANUP] Limpiando sandbox de Docker: deteniendo contenedor '{_DOCKER_CONTAINER}'...")
            try:
                # Detener contenedor rápidamente
                subprocess.run(
                    ["docker", "stop", "-t", "2", _DOCKER_CONTAINER],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                logger.info(f"[CLEANUP] Sandbox Docker detenido con éxito.")
            except Exception as e:
                logger.warning(f"[CLEANUP] No se pudo detener el contenedor Docker: {str(e)}")


