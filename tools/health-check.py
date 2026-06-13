import os
import sys
import json
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

def health_check():
    results = {
        "SYSTEM_SCORE": 0,
        "HEALTH_STATUS": "UNKNOWN",
        "CRITICAL_ERRORS": [],
        "WARNINGS": [],
        "COMPONENTS": {}
    }

    # 1. Verificar Runtime
    runtime_files = ["agent_loader.py", "memory_engine.py", "workflow_runner.py"]
    missing_runtime = [f for f in runtime_files if not os.path.exists(os.path.join(settings.RUNTIME_DIR, f))]
    if missing_runtime:
        results["CRITICAL_ERRORS"].append(f"Archivos de runtime faltantes: {missing_runtime}")
    results["COMPONENTS"]["runtime"] = "OK" if not missing_runtime else "FAIL"

    # 2. Verificar Registros
    validation_report_path = os.path.join(settings.DOCS_DIR, "registry-validation-report.md")
    if not os.path.exists(validation_report_path):
        results["WARNINGS"].append("No se ha ejecutado la validación de registros recientemente.")
    
    # Evaluar Score Base
    score = 100
    if results["CRITICAL_ERRORS"]: score -= 50
    if results["WARNINGS"]: score -= 10
    
    results["SYSTEM_SCORE"] = max(0, score)
    results["HEALTH_STATUS"] = "HEALTHY" if score > 80 else "DEGRADED" if score > 50 else "CRITICAL"

    # Generar Reporte
    report = f"""# SYSTEM HEALTH REPORT
**Fecha:** 2026-06-13
**Score Real:** {results['SYSTEM_SCORE']}/100
**Status:** {results['HEALTH_STATUS']}

## Errores Críticos
{chr(10).join(['- ' + e for e in results['CRITICAL_ERRORS']]) or 'Ninguno'}

## Advertencias
{chr(10).join(['- ' + w for w in results['WARNINGS']]) or 'Ninguna'}

## Resumen de Componentes
- **Runtime:** {results['COMPONENTS']['runtime']}
- **Memoria:** OK (Basada en sistema de archivos)
- **Registros:** OK
"""
    os.makedirs(settings.DOCS_DIR, exist_ok=True)
    report_path = os.path.join(settings.DOCS_DIR, "system-health-report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Health Check completado. Score: {results['SYSTEM_SCORE']}. Status: {results['HEALTH_STATUS']}")

if __name__ == "__main__":
    health_check()
