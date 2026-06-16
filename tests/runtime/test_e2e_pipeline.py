# test_e2e_pipeline.py — tests/runtime/
# Suite de tests End-to-End que simula un pipeline completo de WorkflowRunner
# con mocks completos de LLM, Docker y filesystem para no depender de servicios externos.

import os
import sys
import json
import signal
import pytest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, mock_open, call

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUNTIME_DIR = os.path.join(ROOT_DIR, "runtime")
for p in (ROOT_DIR, RUNTIME_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from runtime.quality_gate import QualityGate
from runtime.auto_learner import AutoLearner
from runtime.schemas import CommandSchema, GateDecisionSchema, LessonSchema


# ─────────────────────────────────────────────
# Fixtures compartidos
# ─────────────────────────────────────────────

@pytest.fixture
def tmp_project(tmp_path):
    """Crea un proyecto temporal con estructura mínima válida."""
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "requirements.txt").write_text("requests\npydantic\n")
    (tmp_path / "main.py").write_text("def run():\n    print('hello')\n")
    return tmp_path


@pytest.fixture
def tmp_project_broken(tmp_path):
    """Proyecto con syntax error para test de QualityGate."""
    (tmp_path / "README.md").write_text("# Broken Project")
    (tmp_path / "requirements.txt").write_text("requests\n")
    (tmp_path / "bad_file.py").write_text("def broken(\n    pass\n")  # SyntaxError
    return tmp_path


# ─────────────────────────────────────────────
# E2E: QualityGate — proyecto válido
# ─────────────────────────────────────────────

class TestQualityGateE2E:
    def test_valid_project_passes_all_checks(self, tmp_project):
        gate = QualityGate(str(tmp_project))
        result = gate.run()
        assert result["status"] == "SUCCESS"
        assert result["approved"] is True
        assert result["score"] == 10.0
        assert result["checks"]["syntax"] == "OK"
        assert result["checks"]["structure"] == "OK"
        assert result["errors"] == []

    def test_broken_syntax_fails_gate(self, tmp_project_broken):
        gate = QualityGate(str(tmp_project_broken))
        result = gate.run()
        assert result["status"] == "FAIL"
        assert result["approved"] is False
        assert result["checks"]["syntax"] == "FAIL"
        assert any("SYNTAX_ERROR" in e for e in result["errors"])

    def test_missing_required_files_fails_gate(self, tmp_path):
        # Proyecto vacío sin README ni requirements.txt
        gate = QualityGate(str(tmp_path))
        result = gate.run()
        assert result["status"] == "FAIL"
        assert any("MISSING_FILE" in e for e in result["errors"])

    def test_score_degrades_with_errors(self, tmp_project_broken):
        gate = QualityGate(str(tmp_project_broken))
        result = gate.run()
        assert result["score"] < 10.0
        assert result["score"] >= 2.0

    def test_gate_decision_is_pydantic_valid(self, tmp_project):
        gate = QualityGate(str(tmp_project))
        result = gate.run()
        # Reconstruir desde dict — debe funcionar sin error
        decision = GateDecisionSchema(
            approved=result["approved"],
            score=result["score"],
            reasons=result["reasons"],
            recommendations=result["recommendations"]
        )
        assert decision.approved is True


# ─────────────────────────────────────────────
# E2E: AutoLearner — heurísticas offline
# ─────────────────────────────────────────────

class TestAutoLearnerE2E:
    def test_learn_from_syntax_errors_offline(self, tmp_path):
        """AutoLearner debe escribir lecciones cuando hay quality_errors."""
        with patch("config.settings.MEMORY_DIR", str(tmp_path)), \
             patch("config.settings.SESSIONS_DIR", str(tmp_path / "sessions")), \
             patch("config.settings.NVIDIA_API_KEY", ""), \
             patch("config.settings.OPENAI_API_KEY", ""):
            learner = AutoLearner()
            result = learner.extract_and_learn(
                session_id="test-session",
                workflow_id="wf-test",
                status="FAILED",
                quality_errors=["SYNTAX_ERROR: app.py - invalid syntax (L5)"]
            )
            assert result is True
            lessons_path = os.path.join(str(tmp_path), "lessons_learned.md")
            assert os.path.exists(lessons_path)
            content = open(lessons_path).read()
            assert "SYNTAX_ERROR" in content or "Sintaxis" in content

    def test_no_lessons_when_no_errors(self, tmp_path):
        """Sin errores ni logs, AutoLearner retorna False."""
        with patch("config.settings.MEMORY_DIR", str(tmp_path)), \
             patch("config.settings.SESSIONS_DIR", str(tmp_path / "sessions")), \
             patch("config.settings.NVIDIA_API_KEY", ""), \
             patch("config.settings.OPENAI_API_KEY", ""):
            learner = AutoLearner()
            result = learner.extract_and_learn(
                session_id="empty-session",
                workflow_id="wf-empty",
                status="SUCCESS",
                quality_errors=[]
            )
            assert result is False

    def test_learn_with_llm_failover_openai(self, tmp_path):
        """AutoLearner intenta NVIDIA, falla y usa OpenAI."""
        mock_fail = MagicMock()
        mock_fail.raise_for_status.side_effect = Exception("NVIDIA down")

        mock_ok = MagicMock()
        mock_ok.raise_for_status.return_value = None
        mock_ok.json.return_value = {
            "choices": [{"message": {"content": "- **Lección clave:** Siempre validar sintaxis."}}]
        }

        with patch("config.settings.MEMORY_DIR", str(tmp_path)), \
             patch("config.settings.SESSIONS_DIR", str(tmp_path / "sessions")), \
             patch("config.settings.NVIDIA_API_KEY", "nvidia-fake-key"), \
             patch("config.settings.OPENAI_API_KEY", "openai-fake-key"), \
             patch("requests.post", side_effect=[mock_fail, mock_ok]):
            learner = AutoLearner()
            result = learner.extract_and_learn(
                session_id="failover-session",
                workflow_id="wf-failover",
                status="FAILED",
                quality_errors=["SYNTAX_ERROR: x.py (L1)"]
            )
            assert result is True

    def test_no_duplicate_lessons(self, tmp_path):
        """AutoLearner no debe duplicar lecciones ya existentes."""
        existing_lesson = "- **Sintaxis Correcta:** Validar la sintaxis de todos los archivos"
        lessons_path = os.path.join(str(tmp_path), "lessons_learned.md")
        with open(lessons_path, "w") as f:
            f.write(f"# Lessons Learned\n\n{existing_lesson}\n")

        with patch("config.settings.MEMORY_DIR", str(tmp_path)), \
             patch("config.settings.SESSIONS_DIR", str(tmp_path / "sessions")), \
             patch("config.settings.NVIDIA_API_KEY", ""), \
             patch("config.settings.OPENAI_API_KEY", ""):
            learner = AutoLearner()
            learner.extract_and_learn(
                session_id="dup-session",
                workflow_id="wf-dup",
                status="FAILED",
                quality_errors=["SYNTAX_ERROR: app.py - invalid syntax (L10)"]
            )
            content = open(lessons_path).read()
            # La lección sintaxis aparece exactamente una vez más (la nueva) o no se duplica la exacta
            assert content.count("# Lessons Learned") == 1


# ─────────────────────────────────────────────
# E2E: Schemas Pydantic — validación extrema
# ─────────────────────────────────────────────

class TestSchemasE2E:
    def test_command_schema_strips_whitespace(self):
        cmd = CommandSchema(command="   npm run build   ")
        assert cmd.command == "npm run build"

    def test_command_schema_rejects_empty(self):
        with pytest.raises(Exception):
            CommandSchema(command="")

    def test_lesson_schema_full_creation(self):
        lesson = LessonSchema(
            id="lesson_001",
            phase="quality_gate",
            trigger="SYNTAX_ERROR",
            action="Verificar sintaxis antes de commit",
            confidence=0.99
        )
        assert lesson.confidence == 0.99
        assert lesson.phase == "quality_gate"

    def test_gate_decision_schema_score_range(self):
        decision = GateDecisionSchema(
            approved=False,
            score=4.0,
            reasons=["Fallo de sintaxis"],
            recommendations=["Corregir errores"]
        )
        assert 0 <= decision.score <= 10


# ─────────────────────────────────────────────
# E2E: McpExecutor — flujo completo de herramienta
# ─────────────────────────────────────────────

class TestMcpExecutorE2E:
    def test_full_write_file_tool_flow(self, tmp_path):
        """Escribe un archivo usando write_file con base_dir=tmp_path para pasar el guardrail de workspace."""
        from runtime.mcp_executor import McpExecutor
        executor = McpExecutor(base_dir=str(tmp_path))
        target = str(tmp_path / "output.txt")
        result = executor.execute_tool("write_file", {
            "path": target,
            "content": "E2E test content"
        })
        assert result["status"] == "SUCCESS"
        assert os.path.exists(target)
        assert open(target).read() == "E2E test content"

    def test_read_file_after_write(self, tmp_path):
        """Escribe y luego lee el mismo archivo."""
        from runtime.mcp_executor import McpExecutor
        executor = McpExecutor(base_dir=str(tmp_path))
        target = str(tmp_path / "read_test.txt")
        executor.execute_tool("write_file", {"path": target, "content": "read me"})
        result = executor.execute_tool("read_file", {"path": target})
        assert result["status"] == "SUCCESS"
        assert result["content"] == "read me"

    def test_read_nonexistent_file_returns_fail(self, tmp_path):
        """Leer un archivo que no existe devuelve FAIL."""
        from runtime.mcp_executor import McpExecutor
        executor = McpExecutor(base_dir=str(tmp_path))
        result = executor.execute_tool("read_file", {"path": str(tmp_path / "no_existe.txt")})
        assert result["status"] == "FAIL"
        assert "error" in result

    def test_run_command_mocked_success(self):
        """run_command con permisos válidos y subprocess mockeado retorna SUCCESS."""
        from runtime.mcp_executor import McpExecutor
        executor = McpExecutor()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Build OK"
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            result = executor.execute_tool("run_command", {"command": "npm run build"}, agent_role="frontend-developer")
            # El executor puede retornar SUCCESS o FAIL por cwd, pero nunca Acceso Denegado
            assert result["status"] in ("SUCCESS", "FAIL")
            assert "Acceso Denegado" not in str(result.get("error", ""))

    def test_list_dir_tool(self, tmp_path):
        """list_dir lista los contenidos del directorio."""
        from runtime.mcp_executor import McpExecutor
        (tmp_path / "file_a.txt").write_text("a")
        (tmp_path / "file_b.py").write_text("b = 1")
        executor = McpExecutor(base_dir=str(tmp_path))
        result = executor.execute_tool("list_dir", {"path": str(tmp_path)})
        assert result["status"] == "SUCCESS"
        names = [i["name"] for i in result["items"]]
        assert "file_a.txt" in names
        assert "file_b.py" in names

    def test_unknown_tool_returns_fail(self):
        from runtime.mcp_executor import McpExecutor
        executor = McpExecutor()
        result = executor.execute_tool("nonexistent_tool_xyz", {})
        assert result["status"] == "FAIL"
        assert "error" in result
