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
    slug = os.path.basename(temp_project)
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(f"# Requisitos del proyecto {slug}\n" + ("a" * 500) + "\nEntrevista validada\n")
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
    res = executor.execute_tool("write_file", {"path": "memory/projects/my-project/requirements.md", "content": "Corto"}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "sobrescritura destructiva" in res["error"]

def test_mcp_executor_secret_protection(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    executor.active_project_name = "my-project"
    
    # Intentar escribir secretos en un archivo .py
    res = executor.execute_tool("write_file", {"path": "app.py", "content": "gemini_api_key = 'AIzaSy1234567890abcdef1234567890abcdef'"}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "No está permitido guardar secretos" in res["error"]

def test_mcp_executor_path_isolation(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    executor.active_project_name = "my-project"
    
    # Intentar escribir a memory/requirements.md directamente (global) sin projects/my-project
    res = executor.execute_tool("write_file", {"path": "memory/requirements.md", "content": "Requisitos globales"}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "Acceso Denegado: Intentaste escribir en la ruta global" in res["error"]

    # Intentar leer de memory/requirements.md directamente
    res = executor.execute_tool("read_file", {"path": "memory/requirements.md"}, agent_role="ceo")
    assert res["status"] == "FAIL"
    assert "Acceso Denegado: Intentaste leer de la ruta global" in res["error"]

def test_quality_gate_anti_contamination_and_coherence(temp_project):
    # Crear carpeta de proyecto anterior (contaminante)
    old_proj_dir = os.path.join(temp_project, "memory", "projects", "edmacars-store")
    os.makedirs(old_proj_dir, exist_ok=True)
    with open(os.path.join(old_proj_dir, "requirements.md"), "w", encoding="utf-8") as f:
        f.write("# Edmacars Store\n")

    # Carpeta del proyecto nuevo
    new_proj_dir = os.path.join(temp_project, "memory", "projects", "proyecto-nuevo-2026")
    os.makedirs(new_proj_dir, exist_ok=True)

    # Caso 1: Contaminación con "edmacars"
    req_path = os.path.join(new_proj_dir, "requirements.md")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("# Proyecto Nuevo 2026\n" + ("a" * 500) + "\nEntrevista validada\nContiene info de edmacars store\n")
    
    res = QualityGate.validate_phase("wf-discovery", new_proj_dir)
    assert res["status"] == "FAIL"
    assert any("Se detectó contaminación de contexto" in err for err in res["errors"])

    # Caso 2: Incoherencia de título (no menciona "proyecto" ni "nuevo" ni "2026")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("# Alguna Otra Tienda\n" + ("a" * 500) + "\nEntrevista validada\n")
    
    res = QualityGate.validate_phase("wf-discovery", new_proj_dir)
    assert res["status"] == "FAIL"
    assert any("no hace referencia al slug" in err for err in res["errors"])

def test_dashboard_persistence(temp_project):
    from runtime.dashboard import update_dashboard_state, get_web_response, STATE_FILE_PATH, _load_state_from_disk
    import runtime.dashboard as db
    
    # Cambiar temporalmente la ruta del archivo de estado
    original_path = db.STATE_FILE_PATH
    db.STATE_FILE_PATH = os.path.join(temp_project, "dashboard_state.json")
    
    try:
        update_dashboard_state({"status": "RUNNING", "project_name": "test-persist"})
        assert os.path.exists(db.STATE_FILE_PATH)
        
        # Cargar de disco en otra variable
        with open(db.STATE_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["status"] == "RUNNING"
        assert data["state"]["project_name"] == "test-persist"
    finally:
        db.STATE_FILE_PATH = original_path


def test_mcp_executor_clean_project_dir(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    executor.active_project_name = "test-project"
    
    # Create project dirs
    project_dir = os.path.join(temp_project, "projects", "test-project")
    sub_dir = os.path.join(project_dir, "web")
    os.makedirs(sub_dir, exist_ok=True)
    
    # Create some mock files
    file1 = os.path.join(sub_dir, "index.js")
    with open(file1, "w") as f:
        f.write("console.log('hello')")
        
    # Verify files exist
    assert os.path.exists(file1)
    
    # Try cleaning the subdirectory
    res = executor.execute_tool("clean_project_dir", {"path": "projects/test-project/web"}, agent_role="frontend-developer")
    assert res["status"] == "SUCCESS"
    assert "clean_project_dir" in res or "message" in res
    
    # Subdirectory contents should be empty, but subdirectory itself still exists
    assert os.path.exists(sub_dir)
    assert len(os.listdir(sub_dir)) == 0

    # Deny cleaning outside sandbox
    res_outside = executor.execute_tool("clean_project_dir", {"path": "projects/other-project"}, agent_role="frontend-developer")
    assert res_outside["status"] == "FAIL"

    # Deny cleaning project root itself
    res_root = executor.execute_tool("clean_project_dir", {"path": "projects/test-project"}, agent_role="frontend-developer")
    assert res_root["status"] == "FAIL"


def test_mcp_executor_mkdir_multi_path(temp_project):
    executor = McpExecutor(base_dir=temp_project)
    
    # Run a mkdir -p with multiple paths
    command = "mkdir -p projects/test-project/web projects/test-project/admin-app"
    res = executor._try_native_command(command, temp_project)
    
    assert res is not None
    assert res["status"] == "SUCCESS"
    
    # Check that both directories were created as separate directories (no space in the name)
    web_dir = os.path.join(temp_project, "projects", "test-project", "web")
    admin_dir = os.path.join(temp_project, "projects", "test-project", "admin-app")
    space_dir = os.path.join(temp_project, "projects", "test-project", "web projects")
    
    assert os.path.exists(web_dir)
    assert os.path.exists(admin_dir)
    assert not os.path.exists(space_dir)

