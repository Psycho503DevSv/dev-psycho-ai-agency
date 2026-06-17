import os
import ast
import json
from typing import List, Dict, Optional

from runtime.logger import logger
from runtime.schemas import GateDecisionSchema
from config import settings

class QualityGate:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.errors = []
        self.registry_path = os.path.join(settings.REGISTRY_DIR, "project-types-registry.json")
        self.project_types = []
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.project_types = data.get("project_types", [])
            except Exception as e:
                logger.warning(f"Error cargando project-types-registry: {e}")

    def detect_project_type(self) -> Optional[Dict]:
        """Detecta el tipo de proyecto basado en los archivos presentes en el project_path."""
        if not os.path.exists(self.project_path):
            return None
        best_match = None
        max_matches = -1
        for pt in self.project_types:
            req_files = pt.get("archivos_requeridos", [])
            if not req_files:
                continue
            matches = sum(1 for f in req_files if os.path.exists(os.path.join(self.project_path, f)))
            if matches > 0 and matches > max_matches:
                max_matches = matches
                best_match = pt
        return best_match

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
        pt = self.detect_project_type()
        if not pt:
            self.errors.append("NO_PROJECT_TYPE_DETECTED: No se pudo auto-detectar un tipo de proyecto válido en el directorio.")
            required_files = ["README.md"]
        else:
            required_files = pt.get("archivos_requeridos", [])
            if "README.md" not in required_files:
                required_files = list(required_files) + ["README.md"]
            logger.info(f"Tipo de proyecto detectado para validación: {pt.get('nombre')} ({pt.get('id')})")
            
        for rf in required_files:
            if not os.path.exists(os.path.join(self.project_path, rf)):
                self.errors.append(f"MISSING_FILE: {rf}")
                passed = False
        return passed

    @staticmethod
    def validate_phase(workflow_id: str, project_memory_dir: str) -> Dict:
        """
        Valida que los entregables de una fase documental (discovery, planning) cumplan
        con las especificaciones mínimas y firmas requeridas.
        """
        errors = []
        if workflow_id == "wf-discovery":
            req_path = os.path.join(project_memory_dir, "requirements.md")
            if not os.path.exists(req_path):
                errors.append(f"El archivo de requisitos no fue creado: {req_path}")
            else:
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if len(content) < 500:
                        errors.append(f"El archivo {req_path} tiene longitud insuficiente ({len(content)}/500 caracteres).")
                    if "Entrevista validada" not in content:
                        errors.append(f"El archivo {req_path} no contiene la firma obligatoria 'Entrevista validada' del CEO.")
                    
                    # 1. Validar coherencia slug <-> título del documento
                    first_header = ""
                    for line in content.splitlines():
                        if line.strip().startswith("# "):
                            first_header = line.strip()[2:].strip().lower()
                            break
                    slug = os.path.basename(project_memory_dir)
                    slug_words = [w for w in slug.split("-") if len(w) > 2]
                    if first_header:
                        has_matching_word = any(word in first_header for word in slug_words)
                        if not has_matching_word:
                            errors.append(f"El título del documento de requisitos ('{first_header}') no hace referencia al slug del proyecto ('{slug}').")
                    else:
                        errors.append("El documento de requisitos debe comenzar con un título principal (ej: '# Proyecto Nuevo 2026').")
                        
                    # 2. Prohibir nombres de negocio/slugs de otros proyectos para evitar contaminación
                    parent_dir = os.path.dirname(project_memory_dir)
                    if os.path.exists(parent_dir):
                        other_slugs = [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d)) and d != slug]
                        for other in other_slugs:
                            keywords = [other, other.replace("-", " "), other.replace("-", "")]
                            parts = other.split("-")
                            if len(parts) > 1 and len(parts[0]) > 3:
                                keywords.append(parts[0])
                            
                            for kw in keywords:
                                if len(kw) > 3 and kw.lower() in content.lower():
                                    errors.append(f"Se detectó contaminación de contexto del proyecto '{other}' (término encontrado: '{kw}') en los requisitos.")
                                    break
                except Exception as e:
                    errors.append(f"Error leyendo {req_path}: {str(e)}")
        elif workflow_id == "wf-planning":
            arch_path = os.path.join(project_memory_dir, "architecture.md")
            if not os.path.exists(arch_path):
                errors.append(f"El archivo de arquitectura no fue creado: {arch_path}")
            else:
                try:
                    with open(arch_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if len(content) < 500:
                        errors.append(f"El archivo {arch_path} tiene longitud insuficiente ({len(content)}/500 caracteres).")
                    if "##" not in content:
                        errors.append(f"El archivo {arch_path} no contiene secciones principales estructuradas (ej. '## Componentes').")
                except Exception as e:
                    errors.append(f"Error leyendo {arch_path}: {str(e)}")
        approved = len(errors) == 0
        return {
            "approved": approved,
            "status": "SUCCESS" if approved else "FAIL",
            "errors": errors,
            "score": 10.0 if approved else 2.0
        }

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
