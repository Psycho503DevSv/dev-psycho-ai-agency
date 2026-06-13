import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

def validate_registries():
    registries = {
        "agents": settings.AGENT_REGISTRY,
        "workflows": settings.WORKFLOW_REGISTRY,
        "mcps": settings.MCP_REGISTRY
    }
    
    report = ["# REGISTRY VALIDATION REPORT\n"]
    errors = 0

    # 1. Validar Agentes
    report.append("## 1. Agentes")
    with open(registries["agents"], 'r', encoding='utf-8-sig') as f:
        agents_data = json.load(f).get("agents", [])
        for a in agents_data:
            path = a.get("instructions")
            # Resolver path relativo a la raíz del proyecto
            full_path = os.path.join(settings.BASE_DIR, path)
            if not os.path.exists(full_path):
                report.append(f"- [FAIL] {a['id']}: Archivo instrucciones no encontrado: `{path}` (Resuelto a `{full_path}`)")
                errors += 1
            else:
                report.append(f"- [OK] {a['id']}")

    # 2. Validar Workflows
    report.append("\n## 2. Workflows")
    agent_ids = [a["id"] for a in agents_data]
    with open(registries["workflows"], 'r', encoding='utf-8-sig') as f:
        workflows = json.load(f).get("workflows", [])
        for wf in workflows:
            for step in wf.get("steps", []):
                if step not in agent_ids:
                    report.append(f"- [FAIL] Workflow `{wf['id']}` referencia agente inexistente: `{step}`")
                    errors += 1
            report.append(f"- [OK] {wf['id']}")

    # 3. Validar MCPs
    report.append("\n## 3. MCPs")
    with open(registries["mcps"], 'r', encoding='utf-8-sig') as f:
        mcps = json.load(f).get("configurations", [])
        for mcp in mcps:
            report.append(f"- [OK] {mcp['id']} ({mcp['type']})")

    report.append(f"\n**Total Errores:** {errors}")
    
    report_path = os.path.join(settings.DOCS_DIR, "registry-validation-report.md")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"Validación completada. Errores: {errors}. Reporte generado en {report_path}")

if __name__ == "__main__":
    validate_registries()
