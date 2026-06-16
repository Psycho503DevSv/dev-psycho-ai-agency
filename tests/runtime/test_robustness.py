# test_robustness.py — tests/runtime/
# Suite de pruebas de robustez para Pydantic schemas, LLM failover y Graceful Shutdown

import os
import sys
import json
import signal
import pytest
from unittest.mock import MagicMock, patch

# Garantizar resolución de imports vía conftest.py
from runtime.schemas import CommandSchema, GateDecisionSchema
from runtime.workflow_runner import WorkflowRunner
from runtime.mcp_executor import McpExecutor

def test_command_schema_validation():
    """Valida que CommandSchema no acepte comandos vacíos y haga strip."""
    with pytest.raises(ValueError):
        CommandSchema(command="")
    
    with pytest.raises(ValueError):
        CommandSchema(command="   ")

    cmd = CommandSchema(command="  python main.py  ")
    assert cmd.command == "python main.py"

def test_gate_decision_schema_validation():
    """Valida los tipos e integridad del GateDecisionSchema."""
    decision = GateDecisionSchema(
        approved=True,
        score=9.5,
        reasons=["Passed everything"],
        recommendations=[]
    )
    assert decision.approved is True
    assert decision.score == 9.5

def test_llm_dynamic_failover():
    """Simula una caída persistente de NVIDIA NIM y verifica el fallback a OpenAI."""
    runner = WorkflowRunner()
    
    # Simular claves en settings
    with patch("config.settings.GEMINI_API_KEY", "gemini_mock_key"), \
         patch("config.settings.OPENAI_API_KEY", "openai_mock_key"):
        
        # Simulamos que requests.post da error para Gemini y responde OK para OpenAI
        mock_response_fail = MagicMock()
        mock_response_fail.raise_for_status.side_effect = Exception("Gemini service down")

        mock_response_ok = MagicMock()
        mock_response_ok.returncode = 200
        mock_response_ok.json.return_value = {
            "choices": [{"message": {"content": "OpenAI Fallback Response"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }

        # Mockear requests.post para retornar error la primera vez y success la segunda
        with patch("requests.post", side_effect=[mock_response_fail, mock_response_fail, mock_response_ok]) as mock_post:
            res = runner._call_llm([{"role": "user", "content": "test"}])
            assert res == "OpenAI Fallback Response"
            # Tuvo 2 intentos fallidos con Gemini y el tercero fue exitoso con OpenAI
            assert mock_post.call_count == 3

def test_graceful_shutdown_docker_cleanup():
    """Verifica que al recibir una interrupción se detenga ordenadamente el contenedor de Docker."""
    runner = WorkflowRunner()
    runner.active_workflow_id = "test-wf"
    runner.active_project_name = "test-proj"
    
    # Mockear cleanup y detener el sys.exit
    with patch.object(runner.mcp_executor, "cleanup") as mock_cleanup, \
         patch("sys.exit") as mock_exit, \
         patch("builtins.open", MagicMock()):
        
        runner._handle_graceful_shutdown(signal.SIGINT, None)
        
        # Comprobar llamada a cleanup
        mock_cleanup.assert_called_once()
        mock_exit.assert_called_once_with(0)

def test_role_based_command_permissions():
    """Valida que la ejecución de comandos esté restringida correctamente según la whitelist de roles."""
    import subprocess
    executor = McpExecutor()

    # Mockear subprocess.run para que no ejecute comandos reales
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "mock output"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result):
        # Frontend developer puede correr npm install
        res_ok = executor.execute_tool("run_command", {"command": "npm install"}, agent_role="frontend-developer")
        # No fallará por permisos (puede fallar por subprocess/mock, pero no da Acceso Denegado de permisos)
        assert "Acceso Denegado" not in str(res_ok.get("error", ""))

        # Frontend developer no puede compilar docker o gradle — este chequeo es ANTES del subprocess
        res_fail = executor.execute_tool("run_command", {"command": "gradle build"}, agent_role="frontend-developer")
        assert res_fail["status"] == "FAIL"
        assert "Acceso Denegado" in res_fail["error"]

        # Backend developer puede correr python y pip
        res_py = executor.execute_tool("run_command", {"command": "python -m pytest"}, agent_role="backend-developer")
        assert "Acceso Denegado" not in str(res_py.get("error", ""))


def test_memory_isolation_by_project():
    """Verifica que McpExecutor resuelva y desvíe correctamente las rutas de memoria por proyecto."""
    executor = McpExecutor()
    executor.active_project_name = "test-project-alpha"
    
    # Simular una ruta base de workspace que contiene la palabra "projects" (simulando bug de Windows/rutas)
    simulated_base_dir = os.path.abspath(os.path.join("C:\\", "Users", "Gammer", "projects", "dev-psycho-ai-agency"))
    executor.base_dir = simulated_base_dir
    
    # Ruta de entrada simulada
    input_path = os.path.join(simulated_base_dir, "memory", "requirements.md")
    project_req_path = executor._resolve_path(input_path)
    
    # Debería contener el subdirectorio del proyecto
    expected_req_path = os.path.abspath(os.path.join(simulated_base_dir, "memory", "projects", "test-project-alpha", "requirements.md"))
    assert os.path.normpath(expected_req_path) == os.path.normpath(project_req_path)
    
    # Archivos globales no deberían desviarse
    global_input_path = os.path.join(simulated_base_dir, "memory", "lessons_learned.md")
    global_lessons_path = executor._resolve_path(global_input_path)
    assert "test-project-alpha" not in global_lessons_path
    assert os.path.normpath(global_input_path) == os.path.normpath(global_lessons_path)


def test_telegram_notifier_missing_credentials():
    """Verifica que el notificador retorne False si faltan credenciales."""
    from runtime.notifier import send_telegram_notification
    with patch("config.settings.TELEGRAM_BOT_TOKEN", ""), \
         patch("config.settings.TELEGRAM_CHAT_ID", ""):
        assert send_telegram_notification("test error") is False


def test_telegram_notifier_success():
    """Verifica que se envíe la petición HTTP y retorne True ante éxito."""
    from runtime.notifier import send_telegram_notification
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    
    with patch("config.settings.TELEGRAM_BOT_TOKEN", "123:abc"), \
         patch("config.settings.TELEGRAM_CHAT_ID", "987654"), \
         patch("requests.post", return_value=mock_resp) as mock_post:
        assert send_telegram_notification("test message") is True
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "sendMessage" in args[0]
        assert kwargs["json"]["chat_id"] == "987654"


def test_telegram_notifier_failure():
    """Verifica que retorne False si la petición HTTP falla."""
    from runtime.notifier import send_telegram_notification
    with patch("config.settings.TELEGRAM_BOT_TOKEN", "123:abc"), \
         patch("config.settings.TELEGRAM_CHAT_ID", "987654"), \
         patch("requests.post", side_effect=Exception("API Error")):
        assert send_telegram_notification("test message") is False



