import os

# Root Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Registry Paths
REGISTRY_DIR = os.path.join(BASE_DIR, "registry")
AGENT_REGISTRY = os.path.join(REGISTRY_DIR, "agent-registry.json")
WORKFLOW_REGISTRY = os.path.join(REGISTRY_DIR, "workflow-registry.json")
MCP_REGISTRY = os.path.join(REGISTRY_DIR, "mcp-registry.json")
TOOL_REGISTRY = os.path.join(REGISTRY_DIR, "tool-registry.json")

# Runtime & Projects
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
RUNTIME_DIR = os.path.join(BASE_DIR, "runtime")
AGENTS_DIR = os.path.join(BASE_DIR, "agents")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# Memory paths
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
MEMORIES_USER = os.path.join(MEMORY_DIR, "user")
MEMORIES_SESSION = os.path.join(MEMORY_DIR, "session")
MEMORIES_REPO = os.path.join(MEMORY_DIR, "repo")
SESSIONS_DIR = os.path.join(MEMORY_DIR, "sessions")
PATTERNS_DIR = os.path.join(MEMORY_DIR, "patterns")

# Standards
STANDARDS_DIR = os.path.join(BASE_DIR, "standards")

# Graphiti & Neo4j Settings
USE_GRAPHITI = os.getenv("USE_GRAPHITI", "false").lower() == "true"
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

def ensure_dirs():
    """Garantiza que la estructura de directorios crítica exista."""
    dirs = [
        REGISTRY_DIR, 
        PROJECTS_DIR, 
        AGENTS_DIR,
        DOCS_DIR,
        MEMORY_DIR, 
        MEMORIES_USER, 
        MEMORIES_SESSION, 
        MEMORIES_REPO,
        SESSIONS_DIR,
        PATTERNS_DIR
    ]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

