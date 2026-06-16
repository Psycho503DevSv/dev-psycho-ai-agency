# conftest.py — tests/runtime/
# Configura sys.path para que pytest (y el IDE) encuentren
# tanto el paquete `runtime` como los módulos sueltos dentro de él.

import sys
import os

# Raíz del proyecto → permite `from runtime.mcp_executor import ...`
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Carpeta runtime → permite `import mcp_executor` directamente
RUNTIME_DIR = os.path.join(ROOT_DIR, "runtime")

for p in (ROOT_DIR, RUNTIME_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)
