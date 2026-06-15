import os
import ast
from typing import List, Dict

from runtime.logger import logger
from runtime.schemas import GateDecisionSchema

class QualityGate:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.errors = []
        self.required_files = ["README.md", "requirements.txt"]


    def validate_syntax(self) -> bool:
        """Valida que todos los archivos .py sean sintácticamente correctos."""
        passed = True
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            ast.parse(f.read())
                    except SyntaxError as e:
                        self.errors.append(f"SYNTAX_ERROR: {file} - {e.msg} (L{e.lineno})")
                        passed = False
        return passed

    def validate_structure(self) -> bool:
        """Valida la presencia de archivos obligatorios."""
        passed = True
        for rf in self.required_files:
            if not os.path.exists(os.path.join(self.project_path, rf)):
                self.errors.append(f"MISSING_FILE: {rf}")
                passed = False
        return passed

    def run(self) -> Dict:
        syntax = self.validate_syntax()
        structure = self.validate_structure()
        
        approved = (syntax and structure)
        score = 10.0 if approved else max(2.0, 10.0 - (len(self.errors) * 2.0))
        
        reasons = []
        recommendations = []
        if not approved:
            reasons = [f"Fallo de control de calidad: {err}" for err in self.errors]
            recommendations = [
                "Corrija los errores de sintaxis indicados." if not syntax else "",
                "Asegúrese de incluir README.md y requirements.txt en la raíz del proyecto." if not structure else ""
            ]
            recommendations = [r for r in recommendations if r]
        else:
            reasons = ["Todos los chequeos de calidad pasaron exitosamente."]
            recommendations = ["El proyecto mantiene los estándares de robustez 10/10."]

        # Validar la decisión usando Pydantic
        decision = GateDecisionSchema(
            approved=approved,
            score=score,
            reasons=reasons,
            recommendations=recommendations
        )

        # Retornamos el diccionario dict-compatible e incluimos logs/checks para retrocompatibilidad
        res = decision.model_dump()
        res["status"] = "SUCCESS" if approved else "FAIL"
        res["errors"] = self.errors
        res["checks"] = {
            "syntax": "OK" if syntax else "FAIL",
            "structure": "OK" if structure else "FAIL"
        }
        return res


if __name__ == "__main__":
    # Prueba rápida
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    gate = QualityGate(path)
    print(gate.run())
