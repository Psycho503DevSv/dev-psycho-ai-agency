import os
import json
import logging
from typing import Dict, List, Optional
from config import settings

logger = logging.getLogger("AgentLoader")

class AgentLoader:
    def __init__(self, base_path: str = None, registry_path: str = None):
        self.base_path = base_path or settings.AGENTS_DIR
        self.registry_path = registry_path or settings.AGENT_REGISTRY
        self.agents: Dict[str, dict] = {}

    def load_agents(self) -> Dict[str, dict]:
        """Carga y valida todos los agentes definidos en el registro."""
        if not os.path.exists(self.registry_path):
            logger.error(f"Registro de agentes no encontrado: {self.registry_path}")
            return {}

        with open(self.registry_path, 'r', encoding='utf-8-sig') as f:
            registry_data = json.load(f)

        for agent_def in registry_data.get("agents", []):
            agent_id = agent_def.get("id")
            if not agent_id:
                continue

            agent_path = os.path.join(self.base_path, agent_id)
            if not os.path.exists(agent_path):
                logger.warning(f"[FAIL] Carpeta del agente {agent_id} no existe en {agent_path}")
                continue

            instructions_path = os.path.join(agent_path, "instructions.md")
            if not os.path.exists(instructions_path):
                logger.warning(f"[FAIL] Instrucciones faltantes para el agente {agent_id}")
                continue

            self.agents[agent_id] = {
                "id": agent_id,
                "role": agent_def.get("role"),
                "path": agent_path,
                "instructions_file": instructions_path,
                "hierarchy": agent_def.get("hierarchy_level"),
                "status": "online"
            }
            logger.info(f"Agente cargado correctamente: {agent_id}")

        return self.agents

    def get_agent_context(self, agent_id: str) -> Optional[Dict]:
        """Construye el contexto operativo para un agente específico."""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        with open(agent["instructions_file"], 'r', encoding='utf-8-sig') as f:
            instructions = f.read()

        return {
            "id": agent["id"],
            "role": agent["role"],
            "instructions": instructions,
            "working_directory": agent["path"]
        }

if __name__ == "__main__":
    loader = AgentLoader()
    loaded = loader.load_agents()
    print(f"Agentes cargados: {list(loaded.keys())}")
