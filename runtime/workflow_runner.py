import os
import json
import logging
from typing import List, Dict
from config import settings

# Intentamos importar componentes del runtime
try:
    from agent_loader import AgentLoader
    from memory_engine import MemoryEngine
    from quality_gate import QualityGate
except ImportError:
    # Si se ejecuta directamente sin configurar el path
    import sys
    sys.path.append(os.path.dirname(__file__))
    from agent_loader import AgentLoader
    from memory_engine import MemoryEngine
    from quality_gate import QualityGate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkflowRunner")

class WorkflowRunner:
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or settings.WORKFLOW_REGISTRY
        self.agent_loader = AgentLoader()
        self.memory = MemoryEngine()
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
                # Simulación de ejecución de paso (Carga de contexto)
                context = self.agent_loader.get_agent_context(agent_id)
                logger.info(f"Ejecutando paso con: {agent_id} ({context['role']})")
                
                # Registrar en memoria
                self.memory.save_memory(workflow_id, {
                    "project": project_name,
                    "step": agent_id,
                    "status": "success",
                    "role": context["role"]
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
            # Si el proyecto aún no existe físicamente (simulación), el gate fallará o debe ser preventivo
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
