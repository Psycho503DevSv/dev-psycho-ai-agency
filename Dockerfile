# =============================================================================
#  Psycho503 Dev AI Agency — Dockerfile
#  Imagen base: Python 3.11 slim (seguridad y ligereza)
#  El agente corre completamente aislado del host. Solo el workspace
#  montado en /workspace es accesible; ningún proceso tiene permisos root.
# =============================================================================

FROM python:3.11-slim

# --------------------------------------------------------------------------- #
#  Metadatos OCI
# --------------------------------------------------------------------------- #
LABEL org.opencontainers.image.title="Psycho503 Dev AI Agency"
LABEL org.opencontainers.image.description="Autonomous AI agent with MCP tools, RAG, and auto-learning"
LABEL org.opencontainers.image.version="1.5.0"
LABEL org.opencontainers.image.source="https://github.com/Psycho503/dev-psycho-ai-agency"

# --------------------------------------------------------------------------- #
#  Variables de entorno del sistema
# --------------------------------------------------------------------------- #
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WORKSPACE=/workspace \
    AGENT_ENV=docker

# --------------------------------------------------------------------------- #
#  Dependencias del sistema (herramientas mínimas para el sandbox)
# --------------------------------------------------------------------------- #
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        jq \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------- #
#  Crear usuario no-root para el agente (principio de mínimo privilegio)
# --------------------------------------------------------------------------- #
RUN groupadd --gid 1001 agentgroup && \
    useradd --uid 1001 --gid agentgroup --shell /bin/bash --create-home agent

# --------------------------------------------------------------------------- #
#  Instalar dependencias Python
# --------------------------------------------------------------------------- #
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --------------------------------------------------------------------------- #
#  Copiar el código fuente del agente
# --------------------------------------------------------------------------- #
COPY . /app/

# --------------------------------------------------------------------------- #
#  Configurar el workspace como directorio de trabajo del agente.
#  El volumen real se monta en runtime vía docker-compose.
# --------------------------------------------------------------------------- #
RUN mkdir -p /workspace && chown -R agent:agentgroup /workspace /app

# --------------------------------------------------------------------------- #
#  Cambiar al usuario no-root
# --------------------------------------------------------------------------- #
USER agent

# --------------------------------------------------------------------------- #
#  Exponer el puerto del dashboard de observabilidad
# --------------------------------------------------------------------------- #
EXPOSE 8050

# --------------------------------------------------------------------------- #
#  Healthcheck: verifica que el dashboard responda
# --------------------------------------------------------------------------- #
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# --------------------------------------------------------------------------- #
#  Punto de entrada por defecto: CLI wizard interactivo
# --------------------------------------------------------------------------- #
CMD ["python", "/app/setup.py"]
