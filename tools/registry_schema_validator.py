import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

def run_validation():
    errors = []
    warnings = []
    
    agent_reg = settings.AGENT_REGISTRY
    workflow_reg = settings.WORKFLOW_REGISTRY
    mcp_reg = settings.MCP_REGISTRY
    
    # 1. Validar Agent Registry
    agent_ids = set()
    if not os.path.exists(agent_reg):
        errors.append(f"Registro de agentes no encontrado: {agent_reg}")
    else:
        try:
            with open(agent_reg, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                
            if "agents" not in data:
                errors.append("agent-registry.json no contiene la clave 'agents'")
            else:
                for idx, agent in enumerate(data["agents"]):
                    # Validar campos obligatorios
                    required = ["id", "role", "status", "instructions", "memory_access", "hierarchy_level"]
                    for req in required:
                        if req not in agent or agent[req] is None or agent[req] == "":
                            errors.append(f"Agente en índice {idx} no tiene el campo requerido '{req}'")
                    
                    agent_id = agent.get("id")
                    if agent_id:
                        if agent_id in agent_ids:
                            errors.append(f"ID de agente duplicado: '{agent_id}'")
                        agent_ids.add(agent_id)
                    
                    # Validar ruta de instrucciones
                    inst = agent.get("instructions")
                    if inst:
                        full_inst_path = os.path.join(settings.BASE_DIR, inst)
                        if not os.path.exists(full_inst_path):
                            errors.append(f"Agente '{agent_id}': El archivo de instrucciones no existe: '{inst}' (Resuelto a '{full_inst_path}')")
        except Exception as e:
            errors.append(f"Error al leer agent-registry.json: {str(e)}")

    # 2. Validar Workflow Registry
    workflow_ids = set()
    if not os.path.exists(workflow_reg):
        errors.append(f"Registro de workflows no encontrado: {workflow_reg}")
    else:
        try:
            with open(workflow_reg, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                
            if "workflows" not in data:
                errors.append("workflow-registry.json no contiene la clave 'workflows'")
            else:
                for idx, wf in enumerate(data["workflows"]):
                    required = ["id", "name", "trigger", "steps", "output_file"]
                    for req in required:
                        if req not in wf or wf[req] is None or wf[req] == "":
                            errors.append(f"Workflow en índice {idx} no tiene el campo requerido '{req}'")
                    
                    wf_id = wf.get("id")
                    if wf_id:
                        if wf_id in workflow_ids:
                            errors.append(f"ID de workflow duplicado: '{wf_id}'")
                        workflow_ids.add(wf_id)
                        
                    steps = wf.get("steps", [])
                    if not isinstance(steps, list):
                        errors.append(f"Workflow '{wf_id}': El campo 'steps' debe ser una lista.")
                    else:
                        for step in steps:
                            if step not in agent_ids:
                                errors.append(f"Workflow '{wf_id}': Referencia a un agente inexistente o no registrado: '{step}'")
        except Exception as e:
            errors.append(f"Error al leer workflow-registry.json: {str(e)}")

    # 3. Validar MCP Registry
    mcp_ids = set()
    if not os.path.exists(mcp_reg):
        errors.append(f"Registro de MCPs no encontrado: {mcp_reg}")
    else:
        try:
            with open(mcp_reg, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                
            if "configurations" not in data:
                errors.append("mcp-registry.json no contiene la clave 'configurations'")
            else:
                for idx, mcp in enumerate(data["configurations"]):
                    required = ["id", "type"]
                    for req in required:
                        if req not in mcp or mcp[req] is None or mcp[req] == "":
                            errors.append(f"MCP en índice {idx} no tiene el campo requerido '{req}'")
                    
                    mcp_id = mcp.get("id")
                    if mcp_id:
                        if mcp_id in mcp_ids:
                            errors.append(f"ID de MCP duplicado: '{mcp_id}'")
                        mcp_ids.add(mcp_id)
                        
                    # Validar agentes autorizados
                    for auth in mcp.get("authorized_agents", []):
                        ag_id = auth.get("agent_id")
                        if ag_id and ag_id not in agent_ids:
                            warnings.append(f"MCP '{mcp_id}': Autoriza al agente '{ag_id}' que no está registrado.")
        except Exception as e:
            errors.append(f"Error al leer mcp-registry.json: {str(e)}")

    # Generar Reporte
    report_lines = [
        "# SCHEMA VALIDATION REPORT",
        f"**Estado General:** {'FAILED' if errors else 'SUCCESS'}",
        f"**Errores Encontrados:** {len(errors)}",
        f"**Advertencias:** {len(warnings)}",
        "\n## Errores Detallados"
    ]
    if errors:
        for err in errors:
            report_lines.append(f"- ❌ {err}")
    else:
        report_lines.append("- Ninguno. Todos los registros cumplen con el esquema y son coherentes.")
        
    report_lines.append("\n## Advertencias Detalladas")
    if warnings:
        for wrn in warnings:
            report_lines.append(f"- ⚠️ {wrn}")
    else:
        report_lines.append("- Ninguna.")

    report_path = os.path.join(settings.DOCS_DIR, "schema-validation-report.md")
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    print(f"Validación terminada. Errores: {len(errors)}, Advertencias: {len(warnings)}. Reporte en {report_path}")
    return len(errors) == 0

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
