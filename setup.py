#!/usr/bin/env python3
"""
=============================================================================
  setup.py  —  Psycho503 Dev AI Agency :: CLI Setup Wizard
=============================================================================
  Wizard interactivo de aprovisionamiento. Guía al usuario a través de:
    1. Comprobación del entorno (Python, Docker, dependencias)
    2. Configuración de las claves de API en .env
    3. Elección del modo de ejecución (local | docker)
    4. Lanzamiento del agente

  Uso:
    python setup.py          → Wizard completo
    python setup.py --check  → Solo verifica el entorno
    python setup.py --run    → Arranca el agente directamente (skips wizard)
=============================================================================
"""

import os
import sys
import shutil
import subprocess
import argparse
import textwrap
from pathlib import Path
# Force UTF-8 encoding on Windows to prevent UnicodeEncodeError in console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ─── Colores ANSI ────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    PURPLE = "\033[95m"

def colored(text: str, *codes: str) -> str:
    return "".join(codes) + text + C.RESET

def ok(msg):    print(colored(f"  ✅  {msg}", C.GREEN))
def warn(msg):  print(colored(f"  ⚠️   {msg}", C.YELLOW))
def err(msg):   print(colored(f"  ❌  {msg}", C.RED))
def info(msg):  print(colored(f"  ℹ️   {msg}", C.CYAN))
def header(msg):
    width = 60
    print()
    print(colored("─" * width, C.PURPLE))
    print(colored(f"  {msg}", C.BOLD + C.WHITE))
    print(colored("─" * width, C.PURPLE))

# ─── Rutas ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"

# ─── Comprobación de entorno ─────────────────────────────────────────────────

def check_python() -> bool:
    version = sys.version_info
    if version >= (3, 9):
        ok(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    err(f"Python {version.major}.{version.minor} detectado. Se requiere Python 3.9+.")
    return False

def check_pip_deps() -> bool:
    required = ["requests", "graphiti-core", "openai", "python-dotenv", "nest-asyncio", "pydantic", "pytest"]
    missing = []
    for pkg in required:
        import importlib.util
        spec = importlib.util.find_spec(pkg.replace("-", "_"))
        if spec is None:
            # Alias especial
            if pkg in ("dotenv", "python-dotenv"):
                spec = importlib.util.find_spec("dotenv")
            if spec is None:
                missing.append(pkg)

    if missing:
        warn(f"Paquetes faltantes: {', '.join(missing)}")
        ans = input(colored("  ¿Instalar ahora? [S/n] > ", C.YELLOW)).strip().lower()
        if ans in ("s", "y", ""):
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)
            ok("Dependencias instaladas correctamente.")
        else:
            err("Instala las dependencias manualmente: pip install -r requirements.txt")
            return False
    else:
        ok("Todas las dependencias Python están instaladas ✓")
    return True

def check_docker() -> bool:
    if shutil.which("docker"):
        try:
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                ok("Docker detectado y activo ✓")
                return True
            else:
                warn("Docker instalado pero el daemon no está corriendo.")
                return False
        except Exception:
            warn("Docker instalado pero no responde.")
            return False
    else:
        warn("Docker no encontrado. El modo Docker no estará disponible.")
        return False

def check_env_file() -> bool:
    if ENV_FILE.exists():
        ok(f"Archivo .env encontrado en {ENV_FILE}")
        return True
    warn(".env no encontrado.")
    return False

def run_environment_check() -> dict:
    header("🔍  VERIFICACIÓN DEL ENTORNO")
    results = {
        "python": check_python(),
        "deps":   check_pip_deps(),
        "docker": check_docker(),
        "env":    check_env_file(),
    }
    header("📊  RESUMEN")
    for name, passed in results.items():
        status = colored("PASS", C.GREEN) if passed else colored("FAIL", C.RED)
        print(f"  {name:<12} → {status}")
    return results

# ─── Configuración de .env ───────────────────────────────────────────────────

API_FIELDS = [
    ("NVIDIA_API_KEY",  "NVIDIA NIM API Key    (deja vacío para usar OpenAI/Anthropic)"),
    ("OPENAI_API_KEY",  "OpenAI API Key        (deja vacío si usas NVIDIA/Anthropic)"),
    ("ANTHROPIC_API_KEY", "Anthropic API Key    (deja vacío si usas NVIDIA/OpenAI)"),
    ("GRAPHITI_URI",    "Neo4j / Graphiti URI  [neo4j://localhost:7687]"),
    ("GRAPHITI_USER",   "Neo4j usuario         [neo4j]"),
    ("GRAPHITI_PASS",   "Neo4j contraseña      [deja vacío si no usas memoria]"),
]

def load_existing_env() -> dict:
    env: dict = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
    return env

def save_env(env: dict):
    lines = [
        "# .env — Generado por setup.py de Psycho503 Dev AI Agency",
        "# NO subas este archivo al repositorio.\n",
    ]
    for k, v in env.items():
        lines.append(f"{k}={v}")
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    ok(f".env guardado en {ENV_FILE}")

def configure_env():
    header("🔑  CONFIGURACIÓN DE CLAVES DE API")
    existing = load_existing_env()

    info("Presiona Enter para mantener el valor actual (mostrado entre corchetes).")
    print()

    new_env = dict(existing)
    for key, label in API_FIELDS:
        current = existing.get(key, "")
        display = f"[{'*' * min(len(current), 8) if current else 'vacío'}]"
        val = input(colored(f"  {label} {display}: ", C.CYAN)).strip()
        if val:
            new_env[key] = val
        elif key not in new_env:
            new_env[key] = ""

    save_env(new_env)

# ─── Selección del modo de ejecución ─────────────────────────────────────────

def choose_run_mode(docker_available: bool) -> str:
    header("🚀  MODO DE EJECUCIÓN")
    options = ["1) Local   — Python directo en esta máquina (rápido, sin aislamiento)"]
    if docker_available:
        options.append("2) Docker  — Contenedor aislado (recomendado para producción)")

    for opt in options:
        print(f"  {opt}")
    print()

    while True:
        choice = input(colored("  Selecciona [1/2] > ", C.CYAN)).strip()
        if choice == "1":
            return "local"
        if choice == "2" and docker_available:
            return "docker"
        warn("Opción inválida, intenta de nuevo.")

# ─── Lanzamiento del agente ───────────────────────────────────────────────────

def launch_local():
    header("▶️   LANZANDO AGENTE EN MODO LOCAL")
    info("Iniciando workflow_runner.py …")
    runner = BASE_DIR / "runtime" / "workflow_runner.py"
    if not runner.exists():
        err(f"No se encontró {runner}")
        sys.exit(1)
    subprocess.run([sys.executable, str(runner)], cwd=str(BASE_DIR))

def launch_docker():
    header("🐳  LANZANDO AGENTE EN MODO DOCKER")
    compose = BASE_DIR / "docker-compose.yml"
    if not compose.exists():
        err("docker-compose.yml no encontrado.")
        sys.exit(1)

    info("Construyendo imagen (puede tardar la primera vez) …")
    subprocess.run(["docker", "compose", "up", "--build", "-d"], cwd=str(BASE_DIR), check=True)
    ok("Contenedor arrancado en segundo plano.")
    info("Dashboard disponible en → http://localhost:8050")
    info("Para ver logs:            docker compose logs -f")
    info("Para detener:             docker compose down")

# ─── Punto de entrada ─────────────────────────────────────────────────────────

def print_banner():
    banner = textwrap.dedent(f"""
    {C.PURPLE}{C.BOLD}
    ╔══════════════════════════════════════════════════════════╗
    ║   🤖  Psycho503 Dev AI Agency  —  Setup Wizard v1.5    ║
    ║   Autonomous AI agent with MCP, RAG & Auto-learning     ║
    ╚══════════════════════════════════════════════════════════╝
    {C.RESET}""")
    try:
        print(banner)
    except UnicodeEncodeError:
        fallback = textwrap.dedent(f"""
        {C.PURPLE}{C.BOLD}
        +----------------------------------------------------------+
        |   [OS]  Psycho503 Dev AI Agency  --  Setup Wizard v1.5   |
        |   Autonomous AI agent with MCP, RAG & Auto-learning     |
        +----------------------------------------------------------+
        {C.RESET}""")
        print(fallback)

def main():
    parser = argparse.ArgumentParser(
        description="Psycho503 Dev AI Agency — CLI Setup Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--check", action="store_true", help="Solo verifica el entorno")
    parser.add_argument("--run",   action="store_true", help="Arranca el agente directamente (modo local)")
    parser.add_argument("--docker", action="store_true", help="Arranca el agente directamente en Docker")
    args = parser.parse_args()

    print_banner()

    # ── Modo solo-check ────────────────────────────────────────────────────── #
    if args.check:
        run_environment_check()
        sys.exit(0)

    # ── Modo arranque rápido ───────────────────────────────────────────────── #
    if args.run:
        launch_local()
        sys.exit(0)

    if args.docker:
        launch_docker()
        sys.exit(0)

    # ── Wizard completo ────────────────────────────────────────────────────── #
    env_results = run_environment_check()

    # Paso 2: Configurar .env si no existe o el usuario quiere actualizarlo
    if not env_results["env"]:
        configure_env()
    else:
        ans = input(colored("\n  ¿Actualizar claves de API? [s/N] > ", C.YELLOW)).strip().lower()
        if ans in ("s", "y"):
            configure_env()

    # Paso 3: Seleccionar modo y lanzar
    mode = choose_run_mode(env_results["docker"])
    if mode == "docker":
        launch_docker()
    else:
        launch_local()


if __name__ == "__main__":
    main()
