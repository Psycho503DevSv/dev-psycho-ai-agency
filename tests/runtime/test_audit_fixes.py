import os
import tempfile
import json
import pytest
from runtime.quality_gate import QualityGate
from runtime.mcp_executor import McpExecutor

@pytest.fixture
def temp_project():
    """Crea un proyecto temporal con archivos mock para pruebas."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_quality_gate_dynamic(temp_project):
    # Crear un proyecto que parezca "web-framework"
    with open(os.path.join(temp_project, "package.json"), "w") as f:
        f.write("{}")
    with open(os.path.join(temp_project, "index.html"), "w") as f:
        f.write("<html></html>")
    with open(os.path.join(temp_project, "README.md"), "w") as f:
        f.write("# Demo Project")

    gate = QualityGate(temp_project)
    pt = gate.detect_project_type()
    assert pt is not None
    assert pt["id"] == "web-framework"

    res = gate.run()
    assert res["status"] == "SUCCESS"

def test_quality_gate_validate_phase(temp_project):
    # Caso 1: Sin archivo
    res = QualityGate.validate_phase("wf-discovery", temp_project)
    assert res["status"] == "FAIL"

    # Caso 2: Archivo corto o sin firma
    req_path = os.path.join(temp_project, "requirements.md")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("Corto")
    res = QualityGate.validate_phase("wf-discovery", temp_project)
    assert res["status"] == "FAIL"

    # Caso 3: Archivo válido con firma
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("# Requisitos del proyecto\n" + ("a" * 500) + "\nEntrevista validada\n")
    res = QualityGate.validate_phase("wf-discovery", temp_project)
    assert res["status"] == "SUCCESS"

def test_mcp_executor_phase_guardrails(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    executor.active_workflow_id = "wf-discovery"
    
    # run_command no está permitida en wf-discovery
    res = executor.execute_tool("run_command", {"command": "npm run dev", "cwd": "."}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "no está permitida" in res["error"]

    # write_file sí está permitida
    res = executor.execute_tool("write_file", {"path": "requirements.md", "content": "Sample"}, agent_role="ceo")
    assert res["status"] == "SUCCESS"

def test_mcp_executor_truncation_protection(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    
    # Escribir requisitos válidos primero
    req_path = os.path.join(temp_project, "memory", "projects", "my-project", "requirements.md")
    os.makedirs(os.path.dirname(req_path), exist_ok=True)
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("Requisitos importantes " * 30 + "Entrevista validada")

    executor.active_project_name = "my-project"
    
    # Intentar truncar el archivo
    res = executor.execute_tool("write_file", {"path": "memory/requirements.md", "content": "Corto"}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "sobrescritura destructiva" in res["error"]

def test_mcp_executor_secret_protection(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    executor.active_project_name = "my-project"
    
    # Intentar escribir secretos en un archivo .py
    res = executor.execute_tool("write_file", {"path": "app.py", "content": "gemini_api_key = 'AIzaSy1234567890abcdef1234567890abcdef'"}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "No está permitido guardar secretos" in res["error"]
