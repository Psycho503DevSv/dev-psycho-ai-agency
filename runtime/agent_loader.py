import os
import json
from typing import Dict, List, Optional
from config import settings

from runtime.logger import logger


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

    def sanitize_prompt_injection(self, text: str) -> str:
        """Sanitiza el texto de entrada para neutralizar ataques comunes de Prompt Injection."""
        import re
        patterns = [
            (r"(?i)\bignore\s+(?:all\s+)?previous\s+instructions\b", "[INJECTION_DETECTOR: INTENTO DE IGNORAR INSTRUCCIONES]"),
            (r"(?i)\bdisregard\s+(?:all\s+)?previous\b", "[INJECTION_DETECTOR: INTENTO DE IGNORAR CONTEXTO]"),
            (r"(?i)\byou\s+are\s+now\s+a\b", "[INJECTION_DETECTOR: INTENTO DE CAMBIO DE ROL]"),
            (r"(?i)(?:^|[^a-zA-Z0-9_])nueva\s+directiva:", "[INJECTION_DETECTOR: INTENTO DE SOBREESCRITURA DE DIRECTIVA]")
        ]
        sanitized = text
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized

    def build_context_for_agent(self, agent_id: str, project_name: Optional[str] = None) -> Optional[Dict]:
        """Construye un contexto filtrado y optimizado para un agente específico, reduciendo tokens."""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        # Cargar instrucciones base del agente
        try:
            with open(agent["instructions_file"], 'r', encoding='utf-8-sig') as f:
                instructions = f.read()
        except Exception as e:
            logger.error(f"Error leyendo instrucciones para {agent_id}: {str(e)}")
            instructions = f"# {agent['role']}\nInstrucciones no disponibles."

        # Mapeo de archivos de memoria relevantes por rol de agente para optimización de tokens
        memory_mapping = {
            "psycho-ceo": ["active_context.md", "project_state.json", "tasks.md", "decisions.md"],
            "agent-evaluator": ["active_context.md", "requirements.md", "architecture.md", "lessons_learned.md"],
            "product-manager": ["active_context.md", "requirements.md", "tasks.md"],
            "frontend": ["active_context.md", "architecture.md", "tasks.md"],
            "backend": ["active_context.md", "architecture.md", "tasks.md"],
            "devops": ["active_context.md", "architecture.md", "tasks.md"],
            "qa": ["active_context.md", "requirements.md", "lessons_learned.md"],
            "security": ["active_context.md", "requirements.md", "lessons_learned.md"],
            "ai-architect": ["active_context.md", "architecture.md", "decisions.md"],
            "mcp-architect": ["active_context.md", "architecture.md", "decisions.md"],
            "rag-architect": ["active_context.md", "architecture.md", "decisions.md"],
            "context-engineer": ["active_context.md", "lessons_learned.md"]
        }

        # Cargar selectivamente memoria compartida
        shared_memory_blocks = []

        # Cargar memoria semántica de Graphiti si está activado
        if settings.USE_GRAPHITI:
            try:
                import asyncio
                from runtime.graphiti_bridge import bridge
                query = f"What is the current project state, details and task list for role {agent_id}?"
                
                loop = None
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    pass

                if loop and loop.is_running():
                    try:
                        import nest_asyncio
                        nest_asyncio.apply()
                        facts = asyncio.run(bridge.search_context(query))
                    except Exception:
                        facts = []
                else:
                    facts = asyncio.run(bridge.search_context(query))

                if facts:
                    sanitized_facts = [self.sanitize_prompt_injection(fact) for fact in facts]
                    shared_memory_blocks.append("### MEMORIA SEMÁNTICA DINÁMICA (GRAPHITI)\n" + "\n".join([f"- {fact}" for fact in sanitized_facts]) + "\n")
            except Exception as e:
                logger.warning(f"No se pudo recuperar memoria semántica de Graphiti para {agent_id}: {str(e)}")

        memory_dir = settings.MEMORY_DIR
        files_to_load = memory_mapping.get(agent_id, ["active_context.md"])

        for filename in files_to_load:
            if project_name and filename not in ["lessons_learned.md"]:
                file_path = os.path.join(memory_dir, "projects", project_name, filename)
            else:
                file_path = os.path.join(memory_dir, filename)
                
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    sanitized_content = self.sanitize_prompt_injection(content)
                    shared_memory_blocks.append(f"### MEMORY: {filename}\n{sanitized_content}\n")
                except Exception as e:
                    logger.warning(f"No se pudo cargar {filename} para {agent_id}: {str(e)}")

        shared_memory_section = "\n## MEMORIA CENTRAL COMPARTIDA (FILTRADA/RELEVANTE)\n" + "\n".join(shared_memory_blocks) if shared_memory_blocks else ""

        # Inyectar memoria al inicio de las instrucciones operativas
        full_instructions = f"{shared_memory_section}\n\n# INSTRUCCIONES OPERATIVAS DEL ROL\n{instructions}"

        return {
            "id": agent["id"],
            "role": agent["role"],
            "instructions": full_instructions,
            "working_directory": agent["path"]
        }

    def get_agent_context(self, agent_id: str, project_name: Optional[str] = None) -> Optional[Dict]:
        """Mantiene compatibilidad con llamadas existentes usando el generador de contexto filtrado."""
        return self.build_context_for_agent(agent_id, project_name)

if __name__ == "__main__":
    loader = AgentLoader()
    loaded = loader.load_agents()
    print(f"Agentes cargados: {list(loaded.keys())}")
