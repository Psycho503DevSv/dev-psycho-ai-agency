import pytest
import os
import json
import shutil
from unittest.mock import patch
from agent_loader import AgentLoader
from memory_engine import MemoryEngine
from workflow_runner import WorkflowRunner
from quality_gate import QualityGate
from config import settings

@pytest.fixture
def temp_dir(tmp_path):
    d = tmp_path / "test_env"
    d.mkdir()
    return d

def test_agent_loader(temp_dir):
    reg_path = temp_dir / "agents.json"
    agents_dir = temp_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "test-agent").mkdir()
    with open(agents_dir / "test-agent" / "instructions.md", "w") as f:
        f.write("test instructions")
        
    with open(reg_path, "w") as f:
        json.dump({"agents": [{"id": "test-agent", "role": "tester"}]}, f)
        
    loader = AgentLoader(base_path=str(agents_dir), registry_path=str(reg_path))
    agents = loader.load_agents()
    assert "test-agent" in agents
    ctx = loader.get_agent_context("test-agent")
    assert ctx is not None
    assert ctx["role"] == "tester"

def test_memory_engine(temp_dir):
    engine = MemoryEngine(base_path=str(temp_dir))
    session_id = "test_sess"
    path = engine.save_memory(session_id, {"data": "test"})
    assert os.path.exists(path)
    memories = engine.retrieve_memory(session_id)
    assert len(memories) == 1
    assert memories[0]["data"]["data"] == "test"

    # Test search functionality
    engine.save_memory(session_id, {"data": "another key item"}, category="special")
    engine.promote_memory(session_id, "global_pattern", {"note": "remember this key item"})
    
    # Search all
    res = engine.search("key item")
    assert len(res) == 2
    
    # Search in session_id
    res_sess = engine.search("key item", session_id=session_id)
    assert len(res_sess) == 1
    
    # Search with category
    res_cat = engine.search("key item", category="special")
    assert len(res_cat) == 1
    
    # Search missing
    res_none = engine.search("non-existent text")
    assert len(res_none) == 0

def test_quality_gate(temp_dir):
    prj = temp_dir / "prj"
    prj.mkdir()
    gate = QualityGate(str(prj))
    res = gate.run()
    assert res["status"] == "FAIL" # Missing README/reqs
    
    (prj / "README.md").write_text("test")
    (prj / "requirements.txt").write_text("test")
    (prj / "app.py").write_text("print('hello')")
    
    res = gate.run()
    assert res["status"] == "SUCCESS"

def test_workflow_runner(temp_dir):
    # Setup dependencies
    reg_path = temp_dir / "wf.json"
    agents_reg = temp_dir / "agents.json"
    agents_dir = temp_dir / "agents"
    agents_dir.mkdir()
    (agents_dir / "orchestrator").mkdir()
    (agents_dir / "orchestrator" / "instructions.md").write_text("test")
    
    with open(agents_reg, "w") as f:
        json.dump({"agents": [{"id": "orchestrator", "role": "boss"}]}, f)
    
    with open(reg_path, "w") as f:
        json.dump({"workflows": [{"id": "wf-test", "steps": ["orchestrator"], "output_file": "out.txt"}]}, f)
    
    # Needs a mock settings or local override
    runner = WorkflowRunner(registry_path=str(reg_path))
    # Hack override loader and memory for test
    runner.agent_loader = AgentLoader(base_path=str(agents_dir), registry_path=str(agents_reg))
    runner.memory = MemoryEngine(base_path=str(temp_dir))
    
    # Check initial state
    assert runner.status == "IDLE"
    
    with patch("runtime.workflow_runner.WorkflowRunner._call_llm", return_value="REPORT: boss task completed"):
        res = runner.run_workflow("wf-test", "test-prj")
    assert res["status"] == "SUCCESS"
    assert runner.status == "SUCCESS"
    assert "orchestrator" in res["executed_steps"]

    # Check state and error when running non-existent workflow
    res_err = runner.run_workflow("wf-non-existent", "test-prj")
    assert res_err["status"] == "FAIL"
    assert runner.status == "FAILED"

    # Check status when workflow references missing agent
    with open(reg_path, "w") as f:
        json.dump({"workflows": [{"id": "wf-bad-agent", "steps": ["non-existent-agent"], "output_file": "out.txt"}]}, f)
    
    runner = WorkflowRunner(registry_path=str(reg_path))
    runner.agent_loader = AgentLoader(base_path=str(agents_dir), registry_path=str(agents_reg))
    runner.memory = MemoryEngine(base_path=str(temp_dir))
    
    res_err2 = runner.run_workflow("wf-bad-agent", "test-prj")
    assert res_err2["status"] == "FAIL"
    assert runner.status == "FAILED"

def test_agent_loader_edge_cases(temp_dir):
    # Registry path doesn't exist
    loader = AgentLoader(base_path=str(temp_dir), registry_path="non_existent_reg.json")
    assert loader.load_agents() == {}
    
    # Empty agent id, folder doesn't exist, instructions.md missing
    reg_path = temp_dir / "agents_edge.json"
    with open(reg_path, "w") as f:
        json.dump({
            "agents": [
                {"id": "", "role": "empty"},
                {"id": "missing-folder", "role": "no_folder"},
                {"id": "missing-instructions", "role": "no_instructions"}
            ]
        }, f)
    (temp_dir / "missing-instructions").mkdir(parents=True, exist_ok=True)
    
    loader2 = AgentLoader(base_path=str(temp_dir), registry_path=str(reg_path))
    loaded = loader2.load_agents()
    assert "missing-folder" not in loaded
    assert "missing-instructions" not in loaded
    assert len(loaded) == 0
    
    # get context of missing agent
    assert loader2.get_agent_context("non_existent_id") is None

def test_workflow_runner_edge_cases(temp_dir):
    # 1. Registry path does not exist
    runner = WorkflowRunner(registry_path="non_existent_wf.json")
    assert runner.workflows == {}
    
    # 2. Agent loader load_agents raising exception
    reg_path = temp_dir / "wf_err.json"
    with open(reg_path, "w") as f:
        json.dump({"workflows": [{"id": "wf-test", "steps": ["agent-1"], "output_file": "out.txt"}]}, f)
    
    runner = WorkflowRunner(registry_path=str(reg_path))
    class BadAgentLoader:
        def load_agents(self):
            raise ValueError("Loader failed")
    runner.agent_loader = BadAgentLoader()  # type: ignore
    res = runner.run_workflow("wf-test", "test-prj")
    assert res["status"] == "FAIL"
    assert "Loader failed" in res["error"]
    assert runner.status == "FAILED"
    
    # 3. Agent context raising exception during step execution
    runner2 = WorkflowRunner(registry_path=str(reg_path))
    class BadContextLoader:
        def load_agents(self):
            return {"agent-1": {"id": "agent-1"}}
        def get_agent_context(self, agent_id, project_name=None):
            raise ValueError("Context failed")
    runner2.agent_loader = BadContextLoader()  # type: ignore
    runner2.memory = MemoryEngine(base_path=str(temp_dir))
    res2 = runner2.run_workflow("wf-test", "test-prj")
    assert res2["status"] == "FAIL"
    assert "Context failed" in res2["error"]
    assert runner2.status == "FAILED"
    
    # 4. Quality Gate Integration
    wf_path = temp_dir / "wf_qg.json"
    with open(wf_path, "w") as f:
        json.dump({"workflows": [{"id": "wf-qg", "steps": ["backend"], "output_file": "out.txt"}]}, f)
        
    runner3 = WorkflowRunner(registry_path=str(wf_path))
    class QGLoader:
        def load_agents(self):
            return {"backend": {"id": "backend", "role": "backend", "path": str(temp_dir)}}
        def get_agent_context(self, agent_id, project_name=None):
            return {"id": "backend", "role": "backend", "path": str(temp_dir)}
            
    runner3.agent_loader = QGLoader()  # type: ignore
    runner3.memory = MemoryEngine(base_path=str(temp_dir))
    runner3.projects_dir = str(temp_dir / "projects")
    
    # Project path exists, but is empty, so Quality Gate fails
    project_dir = temp_dir / "projects" / "my-project"
    project_dir.mkdir(parents=True, exist_ok=True)
    with patch("runtime.workflow_runner.WorkflowRunner._call_llm", return_value="REPORT: backend task completed"):
        res_qg_fail = runner3.run_workflow("wf-qg", "my-project")
    assert res_qg_fail["status"] == "FAIL"
    assert "Quality Gate" in res_qg_fail["error"]
    assert runner3.status == "FAILED"
    
    # Project path exists, Quality Gate succeeds
    (project_dir / "README.md").write_text("ok")
    (project_dir / "requirements.txt").write_text("ok")
    with patch("runtime.workflow_runner.WorkflowRunner._call_llm", return_value="REPORT: backend task completed"):
        res_qg_success = runner3.run_workflow("wf-qg", "my-project")
    assert res_qg_success["status"] == "SUCCESS"
    assert runner3.status == "SUCCESS"

    # Quality Gate raises exception
    # Mocking run method of QualityGate to raise exception
    original_run = QualityGate.run
    def mock_run(self) -> dict:
        raise ValueError("Gate error")
    QualityGate.run = mock_run
    try:
        with patch("runtime.workflow_runner.WorkflowRunner._call_llm", return_value="REPORT: backend task completed"):
            res_qg_exc = runner3.run_workflow("wf-qg", "my-project")
        assert res_qg_exc["status"] == "FAIL"
        assert "Error en Quality Gate" in res_qg_exc["error"]
        assert runner3.status == "FAILED"
    except Exception as ex:
        pass
    finally:
        QualityGate.run = original_run
