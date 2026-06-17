import os
import json
import requests
import signal
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Garantizar resolución de imports agregando el directorio raíz a sys.path
import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError in console
if sys.platform == "win32" and "pytest" not in sys.modules:
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except (AttributeError, io.UnsupportedOperation):
        pass

from config import settings

try:
    from runtime.dashboard import start_dashboard_server, update_dashboard_state, add_dashboard_log, clear_pending_question
except ImportError:
    def start_dashboard_server() -> None: pass
    def update_dashboard_state(state: Dict[str, Any]) -> None: pass
    def add_dashboard_log(log: str) -> None: pass
    def clear_pending_question() -> None: pass


from runtime.logger import logger

# Intentamos importar componentes del runtime
try:
    from agent_loader import AgentLoader
    from memory_engine import MemoryEngine
    from quality_gate import QualityGate
    from mcp_executor import McpExecutor
except ImportError:
    # Si se ejecuta directamente sin configurar el path
    sys.path.append(os.path.dirname(__file__))
    from agent_loader import AgentLoader
    from memory_engine import MemoryEngine
    from quality_gate import QualityGate
    from mcp_executor import McpExecutor


class WorkflowRunner:
    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path or settings.WORKFLOW_REGISTRY
        self.agent_loader = AgentLoader()
        self.memory = MemoryEngine()
        self.mcp_executor = McpExecutor()
        self.workflows: Dict[str, dict] = {}
        self.projects_dir = settings.PROJECTS_DIR
        self.status = "IDLE"
        self.active_workflow_id = None
        self.active_project_name = None
        self.active_steps_completed = []
        self._load_registry()
        
        # Registrar manejadores de interrupciones del sistema (Graceful Shutdown)
        self._setup_shutdown_handlers()

    def _setup_shutdown_handlers(self):
        """Captura señales de interrupción de sistema para apagado ordenado."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, self._handle_graceful_shutdown)
            except ValueError:
                # Ocurre en sub-hilos de Python en ciertas arquitecturas
                pass

    def _handle_graceful_shutdown(self, signum, frame):
        """Bucle de apagado seguro: Libera Docker y persiste el estado interrumpido."""
        logger.warning(f"\n[SHUTDOWN] Interrupción detectada (señal {signum}). Iniciando apagado seguro...")
        self.status = "INTERRUPTED"
        
        # 1. Guardar estado interrumpido a memoria
        if self.active_workflow_id:
            memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
            os.makedirs(memory_dir, exist_ok=True)
            interrupted_file = os.path.join(memory_dir, "interrupted_state.json")
            try:
                with open(interrupted_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "workflow_id": self.active_workflow_id,
                        "project_name": self.active_project_name,
                        "completed_steps": self.active_steps_completed,
                        "timestamp": datetime.now().isoformat() if 'datetime' in globals() else None
                    }, f, indent=2)
                logger.info(f"[SHUTDOWN] Estado del workflow persistido en: {interrupted_file}")
            except Exception as e:
                logger.error(f"[SHUTDOWN] No se pudo guardar el estado de interrupción: {str(e)}")

        # 2. Detener contenedor sandbox si aplica
        try:
            self.mcp_executor.cleanup()
        except Exception as e:
            logger.error(f"[SHUTDOWN] Error durante la limpieza del McpExecutor: {str(e)}")

        # 3. Notificar al dashboard
        try:
            update_dashboard_state({"status": "INTERRUPTED"})
            add_dashboard_log("[SHUTDOWN] Motor del agente interrumpido y cerrado ordenadamente.")
        except Exception:
            pass

        logger.critical("[SHUTDOWN] Liberación completa. Saliendo del proceso.")
        sys.exit(0)


    def _load_registry(self):
        if not os.path.exists(self.registry_path):
            logger.error(f"Falla crítica: Registro de workflows no encontrado en {self.registry_path}")
            return
        with open(self.registry_path, 'r', encoding='utf-8-sig') as f:
            self.workflows = {wf["id"]: wf for wf in json.load(f).get("workflows", [])}

    def _call_llm(self, messages: List[Dict[str, str]], agent_id: Optional[str] = None) -> str:
        """
        Llamada al LLM con rotador inteligente de multi-keys.

        Orden de prioridad:
          1. Gemini  (pool de N keys separadas por coma — rotación diaria + inmediata por cuota)
          2. Groq    (pool de N keys separadas por coma — rotación diaria + inmediata por cuota)
          3. Anthropic (key única)
          4. OpenAI   (key única)
          (NVIDIA NIM reservado solo para auto-aprendizaje, no para agentes)
        """
        import time
        try:
            from runtime.key_rotator import parse_keys, get_active_key, mark_key_exhausted, is_quota_error, is_permanent_error
        except ImportError:
            sys.path.append(os.path.dirname(__file__))
            from key_rotator import parse_keys, get_active_key, mark_key_exhausted, is_quota_error, is_permanent_error

        openai_key = getattr(settings, "OPENAI_API_KEY", "")
        anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        gemini_raw = getattr(settings, "GEMINI_API_KEY", "")
        groq_raw = getattr(settings, "GROQ_API_KEY", "")

        nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")

        gemini_keys = parse_keys(gemini_raw)
        groq_keys = parse_keys(groq_raw)

        is_complex_agent = agent_id in ["psycho-ceo", "product-manager", "ai-architect"]

        # ── Construir la lista de "slots" de proveedores ──
        # P0 Fix: Un slot por cada key Gemini (no solo la activa) para rotación determinística.
        # Si la key activa tiene 403, la siguiente key del slot llega a Groq correctamente.
        provider_slots = []

        # ── Gemini (un slot por cada key del pool) ──
        if gemini_keys:
            gemini_model = getattr(settings, "GEMINI_COMPLEX_MODEL", "gemini-2.5-flash") if is_complex_agent else getattr(settings, "GEMINI_SIMPLE_MODEL", "gemini-2.5-flash-lite")
            for idx, key in enumerate(gemini_keys):
                provider_slots.append({
                    "name": f"Gemini[{idx}]",
                    "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    "key": key,
                    "model": gemini_model,
                    "is_anthropic": False,
                    "pool_name": "gemini",
                    "all_keys": gemini_keys,
                })

        # ── Groq (multi-key con rotador) ──
        if groq_keys:
            groq_model = getattr(settings, "GROQ_COMPLEX_MODEL", "llama-3.3-70b-versatile") if is_complex_agent else getattr(settings, "GROQ_SIMPLE_MODEL", "llama-3.1-8b-instant")
            active_key = get_active_key("groq", groq_keys)
            if active_key:
                provider_slots.append({
                    "name": f"Groq[{groq_keys.index(active_key)}]",
                    "url": "https://api.groq.com/openai/v1/chat/completions",
                    "key": active_key,
                    "model": groq_model,
                    "is_anthropic": False,
                    "pool_name": "groq",
                    "all_keys": groq_keys,
                })

        # ── Anthropic (key única) ──
        if anthropic_key:
            provider_slots.append({
                "name": "Anthropic",
                "url": "https://api.anthropic.com/v1/messages",
                "key": anthropic_key,
                "model": "claude-3-5-sonnet-20241022",
                "is_anthropic": True,
                "pool_name": None,
                "all_keys": [],
            })

        # ── OpenAI (key única) ──
        if openai_key:
            provider_slots.append({
                "name": "OpenAI",
                "url": "https://api.openai.com/v1/chat/completions",
                "key": openai_key,
                "model": "gpt-4o",
                "is_anthropic": False,
                "pool_name": None,
                "all_keys": [],
            })

        # ── NVIDIA NIM (fallback final para agentes) ──
        if nvidia_key:
            provider_slots.append({
                "name": "NVIDIA",
                "url": "https://integrate.api.nvidia.com/v1/chat/completions",
                "key": nvidia_key,
                "model": "meta/llama-3.1-70b-instruct",
                "is_anthropic": False,
                "pool_name": None,
                "all_keys": [],
            })

        if not provider_slots:
            raise ValueError(
                "No hay proveedores de LLM configurados. "
                "Añade al menos GEMINI_API_KEY o GROQ_API_KEY en tu archivo .env "
                "(puedes poner varias separadas por coma)."
            )

        last_exception: Optional[Exception] = None
        # Rastrear qué keys de cada pool ya intentamos en esta llamada
        tried_keys: Dict[str, List[str]] = {"gemini": [], "groq": []}

        # ── Bucle principal: proveedor → reintentos → rotación de key ──
        provider_index = 0
        while provider_index < len(provider_slots):
            provider = provider_slots[provider_index]

            # Si es un pool multi-key, buscar la siguiente key no intentada
            pool_name = provider.get("pool_name")
            all_keys = provider.get("all_keys", [])
            current_key = provider["key"]

            if pool_name and current_key in tried_keys.get(pool_name, []):
                # Esta key ya fue intentada en este ciclo, buscar la siguiente
                next_key = None
                for k in all_keys:
                    if k not in tried_keys[pool_name]:
                        next_key = k
                        break
                if next_key:
                    provider = dict(provider)  # copia para no mutar el slot original
                    provider["key"] = next_key
                    idx = all_keys.index(next_key)
                    provider["name"] = f"{pool_name.capitalize()}[{idx}]"
                else:
                    # Todas las keys del pool agotadas → siguiente proveedor
                    logger.warning(f"[KeyRotator] {pool_name}: Pool completo agotado. Pasando al siguiente proveedor.")
                    provider_index += 1
                    continue

            logger.info(f"Intentando llamada a LLM usando proveedor: {provider['name']} ({provider['model']})")

            if provider.get("is_anthropic"):
                headers = {
                    "x-api-key": provider["key"],
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                }
                system_text = ""
                filtered_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        system_text += msg["content"] + "\n"
                    else:
                        filtered_messages.append(msg)
                payload: Dict[str, Any] = {
                    "model": provider["model"],
                    "messages": filtered_messages,
                    "max_tokens": 4000,
                    "temperature": 0.2,
                }
                if system_text:
                    payload["system"] = system_text.strip()
            elif provider.get("pool_name") == "gemini":
                # P0 Fix: Usar x-goog-api-key (no Authorization: Bearer) para la API de Gemini.
                # Authorization: Bearer causa 403 Forbidden en keys AQ.* de Google AI Studio.
                headers = {
                    "x-goog-api-key": provider["key"],
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": provider["model"],
                    "messages": messages,
                    "temperature": 0.2,
                }
            else:
                headers = {
                    "Authorization": f"Bearer {provider['key']}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": provider["model"],
                    "messages": messages,
                    "temperature": 0.2,
                }

            max_retries = 2
            backoff = 2.0
            success = False

            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        provider["url"], headers=headers, json=payload, timeout=45
                    )
                    response.raise_for_status()
                    res_data = response.json()

                    # ── Contabilizar tokens ──
                    try:
                        usage = res_data.get("usage", {})
                        if provider.get("is_anthropic"):
                            prompt_tokens = usage.get("input_tokens", 0)
                            completion_tokens = usage.get("output_tokens", 0)
                            cost = (prompt_tokens * 0.000003) + (completion_tokens * 0.000015)
                        else:
                            prompt_tokens = usage.get("prompt_tokens", 0)
                            completion_tokens = usage.get("completion_tokens", 0)
                            cost = (prompt_tokens * 0.000005) + (completion_tokens * 0.000015)

                        memory_dir = os.path.join(
                            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory"
                        )
                        os.makedirs(memory_dir, exist_ok=True)
                        token_file = os.path.join(memory_dir, "token_usage.json")
                        accumulated = {
                            "input_tokens": 0, "output_tokens": 0,
                            "estimated_cost_usd": 0.0, "total_calls": 0,
                        }
                        if os.path.exists(token_file):
                            try:
                                with open(token_file, "r") as tf:
                                    accumulated = json.load(tf)
                            except Exception:
                                pass
                        accumulated["input_tokens"] += prompt_tokens
                        accumulated["output_tokens"] += completion_tokens
                        accumulated["estimated_cost_usd"] += cost
                        accumulated["total_calls"] += 1
                        with open(token_file, "w") as tf:
                            json.dump(accumulated, tf)
                        try:
                            from runtime.dashboard import update_dashboard_state
                            update_dashboard_state({
                                "input_tokens": accumulated["input_tokens"],
                                "output_tokens": accumulated["output_tokens"],
                                "estimated_cost_usd": accumulated["estimated_cost_usd"],
                                "total_calls": accumulated["total_calls"],
                            })
                        except Exception:
                            pass
                    except Exception as ex:
                        logger.warning(f"No se pudo guardar métricas de uso de tokens: {str(ex)}")

                    success = True
                    if provider.get("is_anthropic"):
                        return res_data["content"][0]["text"]
                    else:
                        # P0 Fix: safe parse — Gemini a veces retorna content: null o sin content.
                        # En lugar de lanzar KeyError, rotar key o bajar al siguiente proveedor.
                        msg = res_data.get("choices", [{}])[0].get("message", {})
                        text = msg.get("content") or msg.get("text") or ""
                        if not text.strip():
                            success = False
                            logger.warning(
                                f"[{provider['name']}] Respuesta HTTP 200 pero content vacío/null. "
                                f"Rotando al siguiente proveedor."
                            )
                            # Si tiene pool, marcar como agotada temporalmente y rotar
                            if pool_name:
                                mark_key_exhausted(pool_name, all_keys, provider["key"], permanent=False)
                                tried_keys[pool_name].append(provider["key"])
                            break  # Salir del bucle de reintentos; el externo rota
                        return text

                except requests.exceptions.HTTPError as e:
                    last_exception = e
                    status_code = e.response.status_code if e.response is not None else 0
                    error_text = e.response.text if e.response is not None else str(e)

                    # P0 Fix: 403 = key permanentemente inválida — rotar y excluir para siempre.
                    # 429/503 = cuota agotada — rotar y reintentar mañana.
                    if pool_name and is_permanent_error(status_code, error_text):
                        logger.error(
                            f"[KeyRotator] {provider['name']}: Key inválida permanente ({status_code}). "
                            f"Excluida del pool para siempre."
                        )
                        mark_key_exhausted(pool_name, all_keys, provider["key"], permanent=True)
                        if pool_name not in tried_keys:
                            tried_keys[pool_name] = []
                        tried_keys[pool_name].append(provider["key"])
                        break  # Rotar inmediatamente, sin reintentos

                    # ── Rotación inmediata por cuota/rate-limit ──
                    if pool_name and is_quota_error(status_code, error_text):
                        logger.warning(
                            f"[KeyRotator] {provider['name']}: Error de cuota ({status_code}). "
                            f"Rotando a siguiente key del pool '{pool_name}'."
                        )
                        mark_key_exhausted(pool_name, all_keys, provider["key"])
                        if pool_name not in tried_keys:
                            tried_keys[pool_name] = []
                        tried_keys[pool_name].append(provider["key"])
                        break  # Salir del bucle de reintentos; el bucle externo rotará

                    if attempt == max_retries - 1:
                        logger.warning(
                            f"Proveedor {provider['name']} falló tras {max_retries} intentos. "
                            f"Probando fallback..."
                        )
                        break
                    sleep_time = backoff ** (attempt + 1)
                    logger.warning(
                        f"Error en {provider['name']} (intento {attempt+1}/{max_retries}): "
                        f"{str(e)}. Reintentando en {sleep_time}s..."
                    )
                    time.sleep(sleep_time)

                except Exception as e:
                    last_exception = e
                    error_text = str(e)

                    # ── Rotación inmediata por timeout en pool multi-key ──
                    if pool_name and ("timed out" in error_text.lower() or "timeout" in error_text.lower()):
                        logger.warning(
                            f"[KeyRotator] {provider['name']}: Timeout detectado. "
                            f"Rotando key del pool '{pool_name}'."
                        )
                        mark_key_exhausted(pool_name, all_keys, provider["key"])
                        if pool_name not in tried_keys:
                            tried_keys[pool_name] = []
                        tried_keys[pool_name].append(provider["key"])
                        break  # Salir del bucle de reintentos; el bucle externo rotará

                    if attempt == max_retries - 1:
                        logger.warning(
                            f"Proveedor {provider['name']} falló tras {max_retries} intentos. "
                            f"Probando fallback..."
                        )
                        break
                    sleep_time = backoff ** (attempt + 1)
                    logger.warning(
                        f"Error en {provider['name']} (intento {attempt+1}/{max_retries}): "
                        f"{str(e)}. Reintentando en {sleep_time}s..."
                    )
                    time.sleep(sleep_time)

            if success:
                break  # Salida limpia del bucle principal

            # Si el pool tiene más keys sin intentar, NO avanzar el índice de slot
            if pool_name:
                remaining = [k for k in all_keys if k not in tried_keys.get(pool_name, [])]
                if remaining:
                    continue  # Reintentar con la siguiente key del mismo slot

            provider_index += 1  # Pasar al siguiente proveedor/slot

        # Si salimos sin éxito
        logger.error("Fallo definitivo de todos los proveedores de LLM configurados.")
        if last_exception:
            raise last_exception
        raise RuntimeError("Fallo definitivo de todos los proveedores de LLM configurados.")


    def _parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Intenta extraer y parsear un bloque JSON de llamada a herramienta, aplicando auto-corrección."""
        import re
        
        # 1. Intentar buscar bloques delimitados por ```json o ```
        json_str = None
        for pattern in [r"```json\s*(\{.*?\})\s*```", r"```\s*(\{.*?\})\s*```"]:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                break
                
        # 2. Si no hay delimitadores, buscar el primer '{' y el último '}'
        if not json_str:
            match = re.search(r"(\{.*\})", response, re.DOTALL)
            if match:
                json_str = match.group(1).strip()
                
        if not json_str:
            return None
            
        # 3. Intentar parsear el JSON original
        try:
            return json.loads(json_str)
        except Exception:
            pass
            
        # 4. Auto-corrección de errores sintácticos comunes de LLMs
        try:
            cleaned = json_str
            # Comillas simples en llaves: 'key': -> "key":
            cleaned = re.sub(r"'([a-zA-Z0-9_-]+)'\s*:", r'"\1":', cleaned)
            # Comillas simples en valores: : 'value' -> : "value"
            cleaned = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned)
            # Quitar comas sobrantes antes de cierres
            cleaned = re.sub(r",\s*\}", "}", cleaned)
            cleaned = re.sub(r",\s*\]", "]", cleaned)
            # Booleanos/Nulos de Python
            cleaned = cleaned.replace("True", "true").replace("False", "false").replace("None", "null")
            
            return json.loads(cleaned)
        except Exception as e:
            logger.warning(f"Fallo en parseo y auto-corrección de JSON de herramienta: {str(e)}")
            return None

    def _run_agent_loop(self, agent_id: str, context: Dict[str, Any], project_name: str, workflow_id: str, user_request: Optional[str] = None) -> str:
        """Ejecuta un bucle interactivo de agente (Agent Loop) con el LLM y herramientas MCP."""
        system_instruction = f"""Eres el agente '{agent_id}' con el rol de '{context['role']}'.
Tu objetivo principal es asistir en el desarrollo del proyecto '{project_name}'.

Instrucciones operativas de tu rol:
{context.get('instructions', '')}

=== DIRECTRICES DE AUTONOMÍA MCP ===
Puedes usar herramientas locales para cumplir tu objetivo escribiendo un bloque JSON exacto en tu respuesta:
```json
{{
  "tool": "tool_name",
  "arguments": {{"arg1": "value"}}
}}
```

Herramientas disponibles (SOLO estas, NO inventes otras):
- `ask_user`: {{"question": "¿Qué colores prefieres para el diseño de la tienda?"}}
- `read_file`: {{"path": "memory/projects/{project_name}/requirements.md"}}
- `write_file`: {{"path": "memory/projects/{project_name}/requirements.md", "content": "# Requisitos del Proyecto\\n\\n..."}}
- `list_dir`: {{"path": "projects/{project_name}"}}
- `search_code`: {{"query": "const database"}}
- `run_command`: {{"command": "npm run build", "cwd": "projects/{project_name}"}}
- `preview_project`: {{"project_type": "web-framework", "project_path": "projects/{project_name}"}}

IMPORTANTE: Usa `ask_user` para entrevistar al usuario y entender qué proyecto construir. No inventes rutas de placeholders genéricos como 'ruta/relativa' o 'contenido', usa siempre rutas basadas en tu proyecto.
NO uses herramientas como 'Apache Airflow', 'Docker Compose', 'Makefile', 'Python', 'Bash', 'npm' como herramientas MCP — no existen.
Cuando hayas completado todas las tareas del paso, escribe obligatoriamente 'REPORT:' seguido de tu resumen en Markdown."""

        if agent_id == "psycho-ceo" and workflow_id == "wf-discovery":
            system_instruction += f"""

=== PROTOCOLO CENTRAL DEL CEO PARA LA ENTREVISTA ===
1. Al iniciar, debes comprobar si ya existe un archivo de requisitos en 'memory/projects/{project_name}/requirements.md'.
2. Si el archivo no existe o está vacío, debes solicitar al usuario los detalles del proyecto (ej. descripción, propósito, características principales) mediante la herramienta `ask_user`.
3. Con la respuesta del usuario, genera un borrador inicial del archivo de requisitos.
4. Si tienes dudas adicionales sobre el diseño, animaciones, logo o integraciones, usa `ask_user` para aclararlas una por una, construyendo sobre la base y preservando el borrador.
5. Cuando todo esté definido y aclarado con el usuario, escribe el archivo final en 'memory/projects/{project_name}/requirements.md' e incluye de manera obligatoria y visible la frase "Entrevista validada" dentro de los requisitos para autorizar las siguientes fases."""

        user_content = f"Por favor, ejecuta las tareas correspondientes para el paso actual de '{workflow_id}' del proyecto '{project_name}'."
        if user_request:
            user_content += f"\n\nSolicitud inicial del usuario:\n{user_request}"

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ]

        logger.info(f"Iniciando Agent Loop Real para el agente: {agent_id}")
        
        last_response = ""
        previous_tool_calls = []
        
        # Compresión de contexto proactiva
        try:
            try:
                from runtime.context_compressor import ContextCompressor
            except ImportError:
                from context_compressor import ContextCompressor
                
            compressor = ContextCompressor(token_limit=10000)
            messages = compressor.compress_history(messages)
        except Exception as e:
            logger.warning(f"Error comprimiendo historial de contexto antes de llamada: {str(e)}")

        for turn in range(5): # Máximo 5 turnos para prevenir bucles infinitos
            logger.info(f"Bucle de Agente {agent_id} - Turno {turn + 1}/5")
            
            # Notificar al dashboard en vivo
            try:
                update_dashboard_state({
                    "status": "RUNNING",
                    "active_agent": agent_id,
                    "active_role": context.get("role", "Ninguno"),
                    "project_name": project_name,
                    "workflow_id": workflow_id
                })
                add_dashboard_log(f"[{agent_id}] Pensando... Turno {turn + 1}/5")
            except Exception:
                pass

            try:
                response = self._call_llm(messages, agent_id=agent_id)
            except Exception as e:
                logger.error(f"Error llamando al LLM en el turno {turn + 1}: {str(e)}")
                try:
                    add_dashboard_log(f"[{agent_id}] ERROR LLM: {str(e)}")
                except Exception:
                    pass
                raise e

            # Prevenir repeticiones idénticas de respuesta (bucle de alucinación)
            if response.strip() == last_response.strip():
                logger.warning(f"Detección de respuesta repetitiva consecutiva del agente {agent_id}. Rompiendo bucle.")
                try:
                    add_dashboard_log(f"[{agent_id}] Bucle detectado. Cancelando ejecucion.")
                except Exception:
                    pass
                break

            messages.append({"role": "assistant", "content": response})
            last_response = response

            # Buscar llamadas a herramientas usando el parseador robusto
            tool_call = self._parse_tool_call(response)

            # Si el agente intentó llamar una herramienta (tiene backticks o '{') pero falló el parseo, reportar al LLM para autocorrección
            if not tool_call and ("```" in response or "{" in response) and "REPORT:" not in response:
                error_msg = "ERROR: Se detectó un intento de llamada a herramienta pero el formato JSON es inválido. Por favor, asegúrate de responder ÚNICAMENTE con el bloque JSON válido encerrado en triple backticks ```json ... ```."
                logger.warning(f"Agente {agent_id} produjo JSON inválido. Solicitando corrección.")
                try:
                    add_dashboard_log(f"[{agent_id}] Alucinación JSON de herramienta. Solicitando autocorrección.")
                except Exception:
                    pass
                messages.append({"role": "user", "content": error_msg})
                continue

            if tool_call and "tool" in tool_call:
                tool_name = tool_call["tool"]
                tool_args = tool_call.get("arguments", {})
                
                # Prevenir bucles de llamadas a la misma herramienta con mismos argumentos
                call_signature = (tool_name, json.dumps(tool_args, sort_keys=True))
                if call_signature in previous_tool_calls:
                    logger.warning(f"Llamada duplicada consecutiva a herramienta '{tool_name}' con los mismos argumentos.")
                    # Si ya se repitió más de 2 veces, forzar salida para evitar consumo infinito de tokens
                    if previous_tool_calls.count(call_signature) >= 2:
                        logger.error("Bucle de repetición severo detectado. Abortando loop de agente.")
                        try:
                            add_dashboard_log(f"[{agent_id}] Bucle de herramientas detectado. Abortando.")
                        except Exception:
                            pass
                        break
                    
                    messages.append({
                        "role": "user",
                        "content": f"ERROR: Estás intentando llamar consecutivamente a la herramienta '{tool_name}' con los mismos argumentos. Si la acción falló o no tiene cambios, finaliza con 'REPORT:' o cambia de parámetros/herramienta."
                    })
                    previous_tool_calls.append(call_signature)
                    continue

                previous_tool_calls.append(call_signature)
                
                # Ejecutar herramienta vía MCP Executor
                try:
                    add_dashboard_log(f"[{agent_id}] Ejecutando herramienta {tool_name} con args: {json.dumps(tool_args)}")
                except Exception:
                    pass
                agent_role = context.get("role")
                if not isinstance(agent_role, str):
                    agent_role = "agent"
                result = self.mcp_executor.execute_tool(tool_name, tool_args, agent_role=agent_role)
                logger.info(f"Resultado de herramienta {tool_name}: {result['status']}")
                try:
                    add_dashboard_log(f"[{agent_id}] Resultado {tool_name}: {result['status']}")
                except Exception:
                    pass
                
                messages.append({
                    "role": "user",
                    "content": f"RESULTADO DE LA HERRAMIENTA {tool_name}:\n{json.dumps(result, ensure_ascii=False)}"
                })
            else:
                if "REPORT:" in response or turn == 4:
                    if "REPORT:" in response:
                        try:
                            add_dashboard_log(f"[{agent_id}] REPORT: {response.split('REPORT:')[1][:100]}...")
                        except Exception:
                            pass
                    break

        return last_response

    def run_workflow(self, workflow_id: str, project_name: str = "default_project", user_request: Optional[str] = None) -> Dict:
        """Ejecuta la orquestación de un flujo definido."""
        self.status = "RUNNING"
        self.active_workflow_id = workflow_id
        self.active_project_name = project_name
        self.mcp_executor.active_project_name = project_name
        self.mcp_executor.active_workflow_id = workflow_id
        self.active_steps_completed = []

        if project_name in ("default_project", "Ninguno") and "pytest" not in sys.modules:
            logger.info("Esperando a que el usuario cree o seleccione un proyecto en el Dashboard (Gestión de Proyectos)...")
            try:
                update_dashboard_state({"pending_question": "Por favor, selecciona o crea un proyecto activo en el panel 'Gestión de Proyectos' para comenzar."})
            except Exception:
                pass
            import time
            from runtime.dashboard import _state, _lock
            while True:
                with _lock:
                    current_proj = _state.get("project_name")
                if isinstance(current_proj, str) and current_proj not in ("Ninguno", "default_project"):
                    project_name = current_proj
                    self.active_project_name = project_name
                    self.mcp_executor.active_project_name = project_name
                    try:
                        clear_pending_question()
                    except Exception:
                        pass
                    logger.info(f"Proyecto seleccionado desde el dashboard: '{project_name}'. Continuando ejecución.")
                    break
                time.sleep(1.0)
        
        # Crear directorio de memoria aislado para el proyecto
        project_memory_dir = os.path.join(settings.MEMORY_DIR, "projects", project_name)
        os.makedirs(project_memory_dir, exist_ok=True)
        
        # Gate de Autorización con requisitos validados
        if workflow_id in ("wf-planning", "wf-implementation", "wf-build-project"):
            req_path = os.path.join(project_memory_dir, "requirements.md")
            if not os.path.exists(req_path):
                self.status = "FAILED"
                err_msg = f"No se puede iniciar '{workflow_id}' sin haber realizado el descubrimiento. Falta el archivo de requisitos: {req_path}"
                logger.error(err_msg)
                try:
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(f"Fallo: {err_msg}")
                except Exception:
                    pass
                return {"status": "FAIL", "error": err_msg}
            with open(req_path, 'r', encoding='utf-8') as f:
                req_content = f.read()
            if "Entrevista validada" not in req_content:
                self.status = "FAILED"
                err_msg = f"No se puede iniciar '{workflow_id}' porque la entrevista de requisitos no ha sido validada por el CEO. Por favor, ejecuta primero 'wf-discovery' para realizar la entrevista."
                logger.error(err_msg)
                try:
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(f"Fallo: {err_msg}")
                except Exception:
                    pass
                return {"status": "FAIL", "error": err_msg}

        logger.info(f"STATUS CHANGE: {self.status} - Iniciando ejecución de workflow: {workflow_id} para proyecto: {project_name}")
        
        wf = self.workflows.get(workflow_id)
        if not wf:
            self.status = "FAILED"
            logger.error(f"STATUS CHANGE: {self.status} - Workflow no encontrado: {workflow_id}")
            try:
                update_dashboard_state({"status": "FAILED"})
                add_dashboard_log(f"Fallo: Workflow {workflow_id} no encontrado.")
            except Exception:
                pass
            return {"status": "FAIL", "error": "Workflow no encontrado"}

        # Iniciar servidor de dashboard en background de forma automática si no está ya arriba
        try:
            start_dashboard_server()
            update_dashboard_state({
                "status": "RUNNING",
                "project_name": project_name,
                "workflow_id": workflow_id,
                "all_steps": wf.get("steps", []),
                "completed_steps": []
            })
            add_dashboard_log(f"Iniciando workflow: {workflow_id} para {project_name}")
        except Exception as e:
            logger.warning(f"No se pudo iniciar el dashboard server: {str(e)}")
 
        # Validamos agentes
        try:
            loaded_agents = self.agent_loader.load_agents()
        except Exception as e:
            self.status = "FAILED"
            logger.exception(f"STATUS CHANGE: {self.status} - Error cargando agentes: {str(e)}")
            try:
                update_dashboard_state({"status": "FAILED"})
                add_dashboard_log(f"Fallo cargando agentes: {str(e)}")
            except Exception:
                pass
            return {"status": "FAIL", "error": f"Error cargando agentes: {str(e)}"}

        steps_execution = []


        for agent_id in wf.get("steps", []):
            if agent_id not in loaded_agents:
                error_msg = f"Agente requerido {agent_id} no está disponible físicamente."
                logger.error(error_msg)
                self.status = "FAILED"
                logger.info(f"STATUS CHANGE: {self.status} - Paso fallido. Ejecución interrumpida.")
                try:
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(f"Fallo: Agente {agent_id} no disponible.")
                except Exception:
                    pass
                return {"status": "FAIL", "error": error_msg, "completed_steps": steps_execution}
            
            try:
                context = self.agent_loader.get_agent_context(agent_id, project_name, workflow_id)
                if not context:
                    error_msg = f"No se pudo cargar el contexto para el agente {agent_id}"
                    logger.error(error_msg)
                    self.status = "FAILED"
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(error_msg)
                    return {"status": "FAIL", "error": error_msg, "completed_steps": steps_execution}
                logger.info(f"Ejecutando paso con: {agent_id} ({context['role']})")
                
                # Ejecutar Agent Loop real si hay claves configuradas
                gemini_raw = getattr(settings, "GEMINI_API_KEY", "")
                groq_raw = getattr(settings, "GROQ_API_KEY", "")
                nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
                openai_key = getattr(settings, "OPENAI_API_KEY", "")
                anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", "")

                has_provider = bool(gemini_raw or groq_raw or nvidia_key or openai_key or anthropic_key)

                if has_provider:
                    agent_output = self._run_agent_loop(agent_id, context, project_name, workflow_id, user_request=user_request)
                else:
                    logger.warning("Corriendo en MODO SIMULACIÓN: No se configuraron claves de API en el archivo .env.")
                    try:
                        add_dashboard_log(f"[{agent_id}] MODO SIMULACIÓN: Ejecución simulada.")
                    except Exception:
                        pass
                    agent_output = f"SIMULATED REPORT for {agent_id}"

                # Registrar en memoria
                session_log_id = f"{project_name}_{workflow_id}"
                self.memory.save_memory(session_log_id, {
                    "project": project_name,
                    "step": agent_id,
                    "status": "success",
                    "role": context["role"],
                    "output": agent_output
                })

                # --- CHECKPOINT DE HANDOVER ---
                # Validar entregables del paso antes de proceder
                if workflow_id == "wf-discovery":
                    req_path = os.path.join(project_memory_dir, "requirements.md")
                    if not os.path.exists(req_path):
                        raise RuntimeError(f"El paso {agent_id} finalizó pero no existe el archivo obligatorio de requisitos: {req_path}")
                    if agent_id == wf.get("steps", [])[-1]:
                        phase_res = QualityGate.validate_phase(workflow_id, project_memory_dir)
                        if not phase_res["approved"]:
                            raise RuntimeError(f"El entregable final del workflow no cumple los requisitos: {', '.join(phase_res['errors'])}")
                
                elif workflow_id == "wf-planning":
                    arch_path = os.path.join(project_memory_dir, "architecture.md")
                    if not os.path.exists(arch_path):
                        raise RuntimeError(f"El paso {agent_id} finalizó pero no existe el archivo obligatorio de arquitectura: {arch_path}")
                    if agent_id == wf.get("steps", [])[-1]:
                        phase_res = QualityGate.validate_phase(workflow_id, project_memory_dir)
                        if not phase_res["approved"]:
                            raise RuntimeError(f"El entregable final de planificación no cumple los requisitos: {', '.join(phase_res['errors'])}")
                            
                elif workflow_id in ("wf-implementation", "wf-build-project"):
                    if agent_id in ("frontend", "backend"):
                        project_path = os.path.join(self.projects_dir, project_name)
                        if not os.path.exists(project_path):
                            raise RuntimeError(f"El paso {agent_id} finalizó pero no existe la carpeta del proyecto en {project_path}")

                steps_execution.append(agent_id)
                self.active_steps_completed = steps_execution
                try:
                    update_dashboard_state({
                        "completed_steps": list(steps_execution)
                    })
                except Exception:
                    pass

            except Exception as e:
                logger.error(f"Error ejecutando paso {agent_id}: {str(e)}")
                self.status = "FAILED"
                logger.info(f"STATUS CHANGE: {self.status} - Excepción en paso {agent_id}. Ejecución interrumpida.")

                # P3 Fix: Guardar checkpoint parcial para permitir resume desde el paso que falló.
                # Antes solo se guardaba en SIGINT; ahora también en FAIL de un paso.
                try:
                    memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
                    os.makedirs(memory_dir, exist_ok=True)
                    checkpoint_file = os.path.join(memory_dir, "interrupted_state.json")
                    with open(checkpoint_file, "w", encoding="utf-8") as cf:
                        json.dump({
                            "workflow_id": workflow_id,
                            "project_name": project_name,
                            "completed_steps": list(steps_execution),
                            "failed_step": agent_id,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }, cf, indent=2, ensure_ascii=False)
                    logger.info(f"[CHECKPOINT] Estado parcial guardado ({len(steps_execution)} pasos completados). Resume desde: {agent_id}")
                except Exception as ce:
                    logger.warning(f"[CHECKPOINT] No se pudo guardar checkpoint parcial: {ce}")

                try:
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(f"Fallo en paso {agent_id}: {str(e)}")
                except Exception:
                    pass
                return {"status": "FAIL", "error": str(e), "completed_steps": steps_execution, "failed_step": agent_id}


        # Quality Gate Integrado si es implementación o evaluación
        gate_result = None
        
        # 1. Quality Gates para especificaciones de memoria (Discovery y Planning)
        if self.status == "RUNNING" or self.status == "SUCCESS":
            if workflow_id in ("wf-discovery", "wf-planning"):
                phase_res = QualityGate.validate_phase(workflow_id, project_memory_dir)
                if not phase_res["approved"]:
                    self.status = "FAILED"
                    gate_result = phase_res

        # 2. Quality Gate para código (Implementación/Evaluación)
        if (self.status == "RUNNING" or self.status == "SUCCESS") and ("agent-evaluator" in steps_execution or "backend" in steps_execution):
            project_path = os.path.join(self.projects_dir, project_name)
            logger.info(f"Iniciando Quality Gate para {project_path}...")
            try:
                add_dashboard_log("Ejecutando control de calidad QualityGate...")
            except Exception:
                pass
            if os.path.exists(project_path):
                try:
                    gate = QualityGate(project_path)
                    gate_result = gate.run()
                    if gate_result["status"] == "FAIL":
                        logger.warning(f"Quality Gate FAIL: {gate_result['errors']}")
                        self.status = "FAILED"
                        logger.info(f"STATUS CHANGE: {self.status} - Quality Gate fallido.")
                        try:
                            add_dashboard_log("QualityGate: Fallo detectado.")
                        except Exception:
                            pass
                except Exception as e:
                    logger.error(f"Error ejecutando Quality Gate: {str(e)}")
                    self.status = "FAILED"
                    logger.info(f"STATUS CHANGE: {self.status} - Error en Quality Gate.")
            else:
                logger.warning(f"Project path {project_path} no existe. Gate saltado en modo simulación.")

        # Trigger Auto Learner
        try:
            from auto_learner import AutoLearner
            learner = AutoLearner()
            q_errors_raw = gate_result.get("errors", []) if isinstance(gate_result, dict) else []
            q_errors = q_errors_raw if isinstance(q_errors_raw, list) else [str(q_errors_raw)] if q_errors_raw else []
            session_log_id = f"{project_name}_{workflow_id}"
            learner.extract_and_learn(session_id=session_log_id, workflow_id=workflow_id, status=self.status, quality_errors=q_errors)
        except Exception as le:
            logger.warning(f"No se pudo ejecutar el autoaprendizaje al final del workflow: {str(le)}")

        if self.status == "RUNNING":
            self.status = "SUCCESS"

        # Marcar workflow como completado en el dashboard
        try:
            update_dashboard_state({
                "status": "COMPLETED" if self.status == "SUCCESS" else "FAILED",
                "active_agent": "Ninguno",
                "active_role": "Ninguno",
                "next_action": "Siguiente fase: Planificación (wf-planning)" if (workflow_id == "wf-discovery" and self.status == "SUCCESS") else "Listo"
            })
            add_dashboard_log(f"Workflow finalizado con estado: {self.status}")
        except Exception:
            pass

        if self.status == "FAILED":
            try:
                from runtime.notifier import send_telegram_notification
                err_msg = "Error de ejecución de pasos o agentes."
                if gate_result and gate_result.get("errors"):
                    err_msg = "Errores del Quality Gate:\n" + "\n".join([f"• {err}" for err in gate_result.get("errors")])
                elif wf:
                    failed_steps = [s for s in wf.get("steps", []) if s not in steps_execution]
                    if failed_steps:
                        err_msg = f"Fallo al ejecutar el agente/paso: {failed_steps[0]}"
                
                telegram_msg = (
                    f"🚨 <b>Psycho AI DevOS - ALERTA DE FALLO</b> 🚨\n\n"
                    f"<b>Proyecto:</b> <code>{project_name}</code>\n"
                    f"<b>Workflow:</b> <code>{workflow_id}</code>\n"
                    f"<b>Estado Final:</b> <code>{self.status}</code>\n\n"
                    f"<b>Detalle del Error:</b>\n{err_msg}"
                )
                send_telegram_notification(telegram_msg)
            except Exception as ne:
                logger.warning(f"Error enviando notificación Telegram: {str(ne)}")

            return {"status": "FAIL", "error": "Workflow execution failed or Quality Gate errors", "details": gate_result}

        report = {
            "workflow_id": workflow_id,
            "project_name": project_name,
            "status": "SUCCESS",
            "executed_steps": steps_execution,
            "output_expected": wf.get("output_file").format(project_name=project_name) if wf.get("output_file") else None
        }
        
        logger.info(f"STATUS CHANGE: {self.status} - Workflow {workflow_id} finalizado exitosamente.")

        # Auto-handoff discovery -> planning
        if workflow_id == "wf-discovery" and self.status == "SUCCESS":
            logger.info("Discovery finalizado con éxito. Lanzando automáticamente la fase de Planificación (wf-planning)...")
            try:
                add_dashboard_log("Discovery finalizado con éxito. Lanzando automáticamente la fase de Planificación (wf-planning)...")
            except Exception:
                pass
            return self.run_workflow("wf-planning", project_name, user_request)

        return report

def get_existing_projects(base_dir: str) -> List[str]:
    """Obtiene la lista de nombres de proyectos que ya existen en código o memoria."""
    import os
    projects = set()
    for sub in ["projects", "memory/projects"]:
        d = os.path.join(base_dir, sub)
        if os.path.exists(d):
            for item in os.listdir(d):
                if os.path.isdir(os.path.join(d, item)):
                    projects.add(item)
    return sorted(list(projects))

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Psycho503 Dev AI Agency — Workflow Runner")
    parser.add_argument("workflow_id", nargs="?", default="wf-discovery", help="ID del workflow a ejecutar")
    parser.add_argument("project_name", nargs="?", default="demo-project", help="Nombre del proyecto")
    parser.add_argument("--request", "-r", help="Descripción o solicitud inicial del proyecto")
    
    args = parser.parse_args()
    
    project_name = args.project_name
    
    # Si se ejecuta interactivamente y el nombre de proyecto es el de demo/por defecto, preguntar al usuario
    if ("pytest" not in sys.modules) and (project_name == "demo-project"):
        if sys.stdin and hasattr(sys.stdin, 'isatty') and sys.stdin.isatty():
            try:
                print("\n" + "═"*60)
                print("🧠  INICIALIZACIÓN DE PROYECTO — Psycho503 Dev AI Agency")
                print("═"*60)
                
                # Obtener proyectos existentes
                existing = get_existing_projects(ROOT_DIR)
                if existing:
                    print("📁 Proyectos detectados:")
                    for idx, p in enumerate(existing, 1):
                        print(f"  {idx}) {p}")
                    print(f"  N) [Crear nuevo proyecto]")
                    print("═"*60)
                    
                    while True:
                        sel = input("👉 Seleccione un proyecto (número) o 'N' para uno nuevo: ").strip().lower()
                        if sel == 'n':
                            # Pedir nombre de nuevo proyecto
                            while True:
                                name_input = input("✍️ Ingrese el nombre del nuevo proyecto: ").strip()
                                if name_input:
                                    import re
                                    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '-', name_input.lower())
                                    clean_name = re.sub(r'-+', '-', clean_name).strip('-')
                                    if clean_name:
                                        project_name = clean_name
                                        break
                                    else:
                                        print("❌ Nombre de proyecto inválido. Intente de nuevo.")
                                else:
                                    print("❌ El nombre del proyecto no puede estar vacío.")
                            break
                        elif sel.isdigit() and 1 <= int(sel) <= len(existing):
                            project_name = existing[int(sel) - 1]
                            break
                        else:
                            print("❌ Opción inválida. Seleccione un número de la lista o 'N'.")
                else:
                    # No hay proyectos aún, pedir nombre
                    while True:
                        name_input = input("✍️ Ingrese el nombre de su nuevo proyecto: ").strip()
                        if name_input:
                            import re
                            clean_name = re.sub(r'[^a-zA-Z0-9_-]', '-', name_input.lower())
                            clean_name = re.sub(r'-+', '-', clean_name).strip('-')
                            if clean_name:
                                project_name = clean_name
                                break
                            else:
                                print("❌ Nombre de proyecto inválido. Intente de nuevo.")
                        else:
                            print("❌ El nombre del proyecto no puede estar vacío.")
                
                print(f"\n🚀 Iniciando agencia para el proyecto: '{project_name}'")
                print("═"*60 + "\n")
            except (KeyboardInterrupt, EOFError):
                print("\n❌ Operación cancelada por el usuario.")
                sys.exit(0)

    runner = WorkflowRunner()
    result = runner.run_workflow(args.workflow_id, project_name, user_request=args.request)
    print(json.dumps(result, indent=2))
