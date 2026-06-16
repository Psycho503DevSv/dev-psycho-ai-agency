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
    with patch("config.settings.NVIDIA_API_KEY", "nvidia_mock_key"), \
         patch("config.settings.OPENAI_API_KEY", "openai_mock_key"):
        
        # Simulamos que requests.post da error para Nvidia NIM y responde OK para OpenAI
        mock_response_fail = MagicMock()
        mock_response_fail.raise_for_status.side_effect = Exception("Nvidia service down")

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
            # Tuvo 2 intentos fallidos con Nvidia y el tercero fue exitoso con OpenAI
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

