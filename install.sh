#!/usr/bin/env bash
# install.sh — One-click setup script for Linux and macOS

set -e

# Colores ANSI
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0;0m' # No Color

echo -e "${PURPLE}==========================================================${NC}"
echo -e "${PURPLE}   🤖 Psycho503 Dev AI Agency — Setup Installer (Linux/macOS)${NC}"
echo -e "${PURPLE}==========================================================${NC}"

# 1. Check Python version
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${NC}❌ Python no encontrado. Por favor, instala Python 3.9 o superior primero.${NC}"
    exit 1
fi

PY_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "Python detectado: v${PY_VERSION}"

# 2. Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "${CYAN}Creando entorno virtual .venv...${NC}"
    $PYTHON_CMD -m venv .venv
else
    echo -e "${GREEN}Entorno virtual .venv existente encontrado.${NC}"
fi

# 3. Upgrade pip and install dependencies
echo -e "${CYAN}Actualizando pip e instalando dependencias...${NC}"
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
echo -e "${GREEN}Dependencias instaladas con éxito.${NC}"

# 4. Environment File Setup
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${CYAN}Copiando .env.example a .env...${NC}"
        cp .env.example .env
    else
        echo -e "${CYAN}Creando archivo .env vacío...${NC}"
        touch .env
    fi
fi

echo -e "${PURPLE}==========================================================${NC}"
echo -e "${GREEN}✅ Instalación completada con éxito.${NC}"
echo -e "Para iniciar el asistente de configuración interactivo ejecuta:"
echo -e "  ${YELLOW}.venv/bin/python setup.py${NC}"
echo -e "${PURPLE}==========================================================${NC}"
