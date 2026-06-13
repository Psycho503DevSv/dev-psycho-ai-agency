import os
import ast
import logging
from typing import List, Dict

logger = logging.getLogger("QualityGate")

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
        
        status = "SUCCESS" if (syntax and structure) else "FAIL"
        
        return {
            "status": status,
            "errors": self.errors,
            "checks": {
                "syntax": "OK" if syntax else "FAIL",
                "structure": "OK" if structure else "FAIL"
            }
        }

if __name__ == "__main__":
    # Prueba rápida
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    gate = QualityGate(path)
    print(gate.run())
