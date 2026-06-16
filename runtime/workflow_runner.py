import os
import json
import requests
import signal
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError in console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from config import settings

try:
    from runtime.dashboard import start_dashboard_server, update_dashboard_state, add_dashboard_log
except ImportError:
    def start_dashboard_server() -> None: pass
    def update_dashboard_state(state: Dict[str, Any]) -> None: pass
    def add_dashboard_log(log: str) -> None: pass


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

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Realiza una llamada HTTP directa a NVIDIA NIM o OpenAI con reintentos, timeouts y fallback cruzado."""
        nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
        openai_key = getattr(settings, "OPENAI_API_KEY", "")

        # Definir los proveedores configurados disponibles
        providers = []
        if nvidia_key:
            providers.append({
                "name": "NVIDIA NIM",
                "url": "https://integrate.api.nvidia.com/v1/chat/completions",
                "key": nvidia_key,
                "model": "meta/llama-3.1-8b-instruct"
            })
        if openai_key:
            providers.append({
                "name": "OpenAI",
                "url": "https://api.openai.com/v1/chat/completions",
                "key": openai_key,
                "model": "gpt-4o-mini"
            })

        if not providers:
            raise ValueError("No se encontraron claves de API (NVIDIA_API_KEY o OPENAI_API_KEY) en config/settings.")

        # Intentar con los proveedores en secuencia (conmutación por error)
        import time
        last_exception = None

        for provider in providers:
            logger.info(f"Intentando llamada a LLM usando proveedor: {provider['name']} ({provider['model']})")
            headers = {
                "Authorization": f"Bearer {provider['key']}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": provider["model"],
                "messages": messages,
                "temperature": 0.2
            }

            max_retries = 2
            backoff = 2.0

            for attempt in range(max_retries):
                try:
                    response = requests.post(provider["url"], headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                    res_data = response.json()

                    # Procesar y registrar uso de tokens
                    try:
                        usage = res_data.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)

                        memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
                        os.makedirs(memory_dir, exist_ok=True)
                        token_file = os.path.join(memory_dir, "token_usage.json")

                        accumulated = {"input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0, "total_calls": 0}
                        if os.path.exists(token_file):
                            try:
                                with open(token_file, 'r') as tf:
                                    accumulated = json.load(tf)
                            except Exception:
                                pass

                        accumulated["input_tokens"] += prompt_tokens
                        accumulated["output_tokens"] += completion_tokens
                        accumulated["estimated_cost_usd"] += cost
                        accumulated["total_calls"] += 1

                        with open(token_file, 'w') as tf:
                            json.dump(accumulated, tf)

                        try:
                            from runtime.dashboard import update_dashboard_state
                            update_dashboard_state({
                                "input_tokens": accumulated["input_tokens"],
                                "output_tokens": accumulated["output_tokens"],
                                "estimated_cost_usd": accumulated["estimated_cost_usd"],
                                "total_calls": accumulated["total_calls"]
                            })
                        except Exception:
                            pass
                    except Exception as ex:
                        logger.warning(f"No se pudo guardar métricas de uso de tokens: {str(ex)}")

                    return res_data["choices"][0]["message"]["content"]

                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.warning(f"Proveedor {provider['name']} falló tras {max_retries} intentos. Probando fallback si está disponible...")
                        break
                    sleep_time = backoff ** (attempt + 1)
                    logger.warning(f"Error en {provider['name']} (intento {attempt + 1}/{max_retries}): {str(e)}. Reintentando en {sleep_time}s...")
                    time.sleep(sleep_time)


        # Si salimos de los bucles sin retornar, todos fallaron
        logger.error(f"Fallo definitivo de todos los proveedores de LLM configurados.")
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

    def _run_agent_loop(self, agent_id: str, context: Dict[str, Any], project_name: str, workflow_id: str) -> str:
        """Ejecuta un bucle interactivo de agente (Agent Loop) con el LLM y herramientas MCP."""
        system_instruction = (
            f"Eres el agente '{agent_id}' con el rol de '{context['role']}'.\n"
            f"Tu objetivo principal es asistir en el desarrollo del proyecto '{project_name}'.\n\n"
            f"Instrucciones operativas de tu rol:\n{context.get('instructions', '')}\n\n"
            "=== DIRECTRICES DE AUTONOMÍA MCP ===\n"
            "Puedes usar herramientas locales para cumplir tu objetivo escribiendo un bloque JSON exacto en tu respuesta:\n"
            "```json\n"
            "{\n"
            "  \"tool\": \"tool_name\",\n"
            "  \"arguments\": {\"arg1\": \"value\"}\n"
            "}\n"
            "```\n\n"
            "Herramientas disponibles:\n"
            "- `read_file`: {\"path\": \"ruta/relativa\"}\n"
            "- `write_file`: {\"path\": \"ruta/relativa\", \"content\": \"contenido\"}\n"
            "- `list_dir`: {\"path\": \"ruta/relativa\"}\n"
            "- `run_command`: {\"command\": \"comando_de_consola\", \"cwd\": \"directorio\"}\n\n"
            "Cuando hayas completado todas las tareas del paso, escribe obligatoriamente 'REPORT:' seguido de tu resumen en Markdown."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Por favor, ejecuta las tareas correspondientes para el paso actual de '{workflow_id}' del proyecto '{project_name}'."}
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
                response = self._call_llm(messages)
            except Exception as e:
                logger.error(f"Error llamando al LLM en el turno {turn + 1}: {str(e)}")
                try:
                    add_dashboard_log(f"[{agent_id}] ERROR LLM: {str(e)}")
                except Exception:
                    pass
                break

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

    def run_workflow(self, workflow_id: str, project_name: str = "default_project") -> Dict:
        """Ejecuta la orquestación de un flujo definido."""
        self.status = "RUNNING"
        self.active_workflow_id = workflow_id
        self.active_project_name = project_name
        self.active_steps_completed = []
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
                context = self.agent_loader.get_agent_context(agent_id)
                if not context:
                    error_msg = f"No se pudo cargar el contexto para el agente {agent_id}"
                    logger.error(error_msg)
                    self.status = "FAILED"
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(error_msg)
                    return {"status": "FAIL", "error": error_msg, "completed_steps": steps_execution}
                logger.info(f"Ejecutando paso con: {agent_id} ({context['role']})")
                
                # Ejecutar Agent Loop real si hay claves configuradas
                nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
                openai_key = getattr(settings, "OPENAI_API_KEY", "")
                
                if nvidia_key or openai_key:
                    agent_output = self._run_agent_loop(agent_id, context, project_name, workflow_id)
                else:
                    logger.warning("Corriendo en MODO SIMULACIÓN: No se configuraron claves de API en el archivo .env.")
                    try:
                        add_dashboard_log(f"[{agent_id}] MODO SIMULACIÓN: Ejecución simulada.")
                    except Exception:
                        pass
                    agent_output = f"SIMULATED REPORT for {agent_id}"

                # Registrar en memoria
                self.memory.save_memory(workflow_id, {
                    "project": project_name,
                    "step": agent_id,
                    "status": "success",
                    "role": context["role"],
                    "output": agent_output
                })
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
                try:
                    update_dashboard_state({"status": "FAILED"})
                    add_dashboard_log(f"Fallo en paso {agent_id}: {str(e)}")
                except Exception:
                    pass
                return {"status": "FAIL", "error": str(e), "completed_steps": steps_execution}

        # Quality Gate Integrado si es implementación o evaluación
        gate_result = None
        if "agent-evaluator" in steps_execution or "backend" in steps_execution:
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
            q_errors = gate_result["errors"] if gate_result else None
            learner.extract_and_learn(session_id=workflow_id, workflow_id=workflow_id, status=self.status, quality_errors=q_errors)
        except Exception as le:
            logger.warning(f"No se pudo ejecutar el autoaprendizaje al final del workflow: {str(le)}")

        # Marcar workflow como completado en el dashboard
        try:
            update_dashboard_state({
                "status": "COMPLETED" if self.status == "RUNNING" else "FAILED",
                "active_agent": "Ninguno",
                "active_role": "Ninguno"
            })
            add_dashboard_log(f"Workflow finalizado con estado: {self.status}")
        except Exception:
            pass

        if self.status == "FAILED":
            return {"status": "FAIL", "error": "Workflow execution failed or Quality Gate errors", "details": gate_result}

        report = {
            "workflow_id": workflow_id,
            "project_name": project_name,
            "status": "SUCCESS",
            "executed_steps": steps_execution,
            "output_expected": wf.get("output_file").format(project_name=project_name)
        }
        
        self.status = "SUCCESS"
        logger.info(f"STATUS CHANGE: {self.status} - Workflow {workflow_id} finalizado exitosamente.")
        return report

if __name__ == "__main__":
    import sys
    runner = WorkflowRunner()
    wf_id = sys.argv[1] if len(sys.argv) > 1 else "wf-discovery"
    prj_name = sys.argv[2] if len(sys.argv) > 2 else "demo-project"
    result = runner.run_workflow(wf_id, prj_name)
    print(json.dumps(result, indent=2))
