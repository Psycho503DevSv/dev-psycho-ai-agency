import os
import json
import logging
import requests
from typing import List, Dict, Any
from config import settings

# Intentamos importar componentes del runtime
try:
    from agent_loader import AgentLoader
    from memory_engine import MemoryEngine
    from quality_gate import QualityGate
    from mcp_executor import McpExecutor
except ImportError:
    # Si se ejecuta directamente sin configurar el path
    import sys
    sys.path.append(os.path.dirname(__file__))
    from agent_loader import AgentLoader
    from memory_engine import MemoryEngine
    from quality_gate import QualityGate
    from mcp_executor import McpExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkflowRunner")

class WorkflowRunner:
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or settings.WORKFLOW_REGISTRY
        self.agent_loader = AgentLoader()
        self.memory = MemoryEngine()
        self.mcp_executor = McpExecutor()
        self.workflows: Dict[str, dict] = {}
        self.projects_dir = settings.PROJECTS_DIR
        self.status = "IDLE"
        self._load_registry()

    def _load_registry(self):
        if not os.path.exists(self.registry_path):
            logger.error(f"Falla crítica: Registro de workflows no encontrado en {self.registry_path}")
            return
        with open(self.registry_path, 'r', encoding='utf-8-sig') as f:
            self.workflows = {wf["id"]: wf for wf in json.load(f).get("workflows", [])}

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Realiza una llamada HTTP directa a NVIDIA NIM o OpenAI."""
        nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
        openai_key = getattr(settings, "OPENAI_API_KEY", "")

        if nvidia_key:
            api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            api_key = nvidia_key
            model_name = "meta/llama-3.1-8b-instruct"
        elif openai_key:
            api_url = "https://api.openai.com/v1/chat/completions"
            api_key = openai_key
            model_name = "gpt-4o-mini"
        else:
            raise ValueError("No se encontraron claves de API (NVIDIA_API_KEY o OPENAI_API_KEY) en config/settings.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.2
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

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
        for turn in range(5): # Máximo 5 turnos para prevenir bucles infinitos
            logger.info(f"Bucle de Agente {agent_id} - Turno {turn + 1}/5")
            try:
                response = self._call_llm(messages)
            except Exception as e:
                logger.error(f"Error llamando al LLM en el turno {turn + 1}: {str(e)}")
                break

            messages.append({"role": "assistant", "content": response})
            last_response = response

            # Buscar llamadas a herramientas
            tool_call = None
            if "```json" in response:
                try:
                    start = response.find("```json") + 7
                    end = response.find("```", start)
                    json_str = response[start:end].strip()
                    tool_call = json.loads(json_str)
                except Exception as pe:
                    logger.warning(f"Error parseando JSON de herramienta del agente: {str(pe)}")

            if tool_call and "tool" in tool_call:
                tool_name = tool_call["tool"]
                tool_args = tool_call.get("arguments", {})
                
                # Ejecutar herramienta vía MCP Executor
                result = self.mcp_executor.execute_tool(tool_name, tool_args)
                logger.info(f"Resultado de herramienta {tool_name}: {result['status']}")
                
                messages.append({
                    "role": "user",
                    "content": f"RESULTADO DE LA HERRAMIENTA {tool_name}:\n{json.dumps(result, ensure_ascii=False)}"
                })
            else:
                if "REPORT:" in response or turn == 4:
                    break

        return last_response

    def run_workflow(self, workflow_id: str, project_name: str = "default_project") -> Dict:
        """Ejecuta la orquestación de un flujo definido."""
        self.status = "RUNNING"
        logger.info(f"STATUS CHANGE: {self.status} - Iniciando ejecución de workflow: {workflow_id} para proyecto: {project_name}")
        
        wf = self.workflows.get(workflow_id)
        if not wf:
            self.status = "FAILED"
            logger.error(f"STATUS CHANGE: {self.status} - Workflow no encontrado: {workflow_id}")
            return {"status": "FAIL", "error": "Workflow no encontrado"}
 
        # Validamos agentes
        try:
            loaded_agents = self.agent_loader.load_agents()
        except Exception as e:
            self.status = "FAILED"
            logger.exception(f"STATUS CHANGE: {self.status} - Error cargando agentes: {str(e)}")
            return {"status": "FAIL", "error": f"Error cargando agentes: {str(e)}"}

        steps_execution = []

        for agent_id in wf.get("steps", []):
            if agent_id not in loaded_agents:
                error_msg = f"Agente requerido {agent_id} no está disponible físicamente."
                logger.error(error_msg)
                self.status = "FAILED"
                logger.info(f"STATUS CHANGE: {self.status} - Paso fallido. Ejecución interrumpida.")
                return {"status": "FAIL", "error": error_msg, "completed_steps": steps_execution}
            
            try:
                context = self.agent_loader.get_agent_context(agent_id)
                logger.info(f"Ejecutando paso con: {agent_id} ({context['role']})")
                
                # Ejecutar Agent Loop real si hay claves configuradas
                nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
                openai_key = getattr(settings, "OPENAI_API_KEY", "")
                
                if nvidia_key or openai_key:
                    agent_output = self._run_agent_loop(agent_id, context, project_name, workflow_id)
                else:
                    logger.warning("Corriendo en MODO SIMULACIÓN: No se configuraron claves de API en el archivo .env.")
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
            except Exception as e:
                logger.error(f"Error ejecutando paso {agent_id}: {str(e)}")
                self.status = "FAILED"
                logger.info(f"STATUS CHANGE: {self.status} - Excepción en paso {agent_id}. Ejecución interrumpida.")
                return {"status": "FAIL", "error": str(e), "completed_steps": steps_execution}

        # Quality Gate Integrado si es implementación o evaluación
        gate_result = None
        if "agent-evaluator" in steps_execution or "backend" in steps_execution:
            project_path = os.path.join(self.projects_dir, project_name)
            logger.info(f"Iniciando Quality Gate para {project_path}...")
            if os.path.exists(project_path):
                try:
                    gate = QualityGate(project_path)
                    gate_result = gate.run()
                    if gate_result["status"] == "FAIL":
                        logger.warning(f"Quality Gate FAIL: {gate_result['errors']}")
                        self.status = "FAILED"
                        logger.info(f"STATUS CHANGE: {self.status} - Quality Gate fallido.")
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
