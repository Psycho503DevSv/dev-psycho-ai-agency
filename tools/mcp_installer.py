import os
import sys
import json
import subprocess
import logging
from typing import Dict, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("MCP-Installer")

class MCPInstaller:
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or settings.MCP_REGISTRY
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8-sig") as f:
                self.registry = json.load(f)
        else:
            self.registry = {"last_update": "", "configurations": []}

    def save_registry(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2)

    def register_mcp(self, mcp_data: Dict):
        """Registra o actualiza un MCP en el registro."""
        mcp_id = mcp_data.get("id")
        existing = next((m for m in self.registry["configurations"] if m["id"] == mcp_id), None)
        
        if existing:
            existing.update(mcp_data)
            logger.info(f"Actualizado MCP: {mcp_id}")
        else:
            self.registry["configurations"].append(mcp_data)
            logger.info(f"Registrado nuevo MCP: {mcp_id}")
        
        self.save_registry()

    def check_tool_installed(self, command: str) -> bool:
        """Verifica si una herramienta de sistema (docker, git, etc) está instalada."""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except:
            return False

    def install_standard_mcps(self):
        """Configura los MCPs estándar basados en la realidad del sistema."""
        
        # 1. Git
        git_status = "OPERATIONAL" if self.check_tool_installed("git") else "FAILED"
        self.register_mcp({
            "id": "git",
            "type": "core",
            "status": git_status,
            "transport": "stdio",
            "capabilities": ["read", "commit", "push"]
        })

        # 2. Docker
        docker_status = "OPERATIONAL" if self.check_tool_installed("docker") else "FAILED"
        self.register_mcp({
            "id": "docker",
            "type": "infrastructure",
            "status": docker_status,
            "transport": "stdio",
            "capabilities": ["container-mgmt", "image-mgmt"]
        })

        # 3. Fetch
        self.register_mcp({
            "id": "fetch",
            "type": "web",
            "status": "OPERATIONAL",
            "transport": "http",
            "capabilities": ["web-scraping", "api-fetch"]
        })

        # 4. Playwright
        self.register_mcp({
            "id": "playwright",
            "type": "browser",
            "status": "CONFIGURED",
            "transport": "stdio",
            "capabilities": ["browser-automation", "testing"]
        })

if __name__ == "__main__":
    installer = MCPInstaller()
    installer.install_standard_mcps()
    print("Instalación y registro de MCPs inicializado.")
