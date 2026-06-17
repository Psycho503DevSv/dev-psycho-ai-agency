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
        # Priorizar nextjs-monorepo colocándolo al principio de la lista de evaluación
        ordered_types = sorted(self.project_types, key=lambda x: 0 if x.get("id") == "nextjs-monorepo" else 1)
        for pt in ordered_types:
            req_files = pt.get("archivos_requeridos", [])
            if not req_files:
                continue
            
            # Buscar cada archivo requerido en el proyecto (incluso en subcarpetas)
            matches = 0
            for rf in req_files:
                # Si existe directamente en la raíz
                if os.path.exists(os.path.join(self.project_path, rf)):
                    matches += 1
                else:
                    # Buscar de forma recursiva
                    found = False
                    for root, _, files in os.walk(self.project_path):
                        if rf in files:
                            found = True
                            break
                    if found:
                        matches += 1
                        
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
            # README.md siempre debe estar estrictamente en la raíz del proyecto
            if rf == "README.md":
                if not os.path.exists(os.path.join(self.project_path, rf)):
                    self.errors.append(f"MISSING_FILE: {rf}")
                    passed = False
            else:
                # Otros archivos pueden estar en subcarpetas (ej. package.json en web/)
                if os.path.exists(os.path.join(self.project_path, rf)):
                    continue
                found = False
                for root, _, files in os.walk(self.project_path):
                    if rf in files:
                        found = True
                        break
                if not found:
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
                    if len(content) < 200:
                        errors.append(f"El archivo {req_path} tiene longitud insuficiente ({len(content)}/200 caracteres mínimos).")
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
                    # P2 Fix: Filtrar palabras genéricas del español/inglés que no identifican proyectos
                    # (ej: slug 'proyecto-nuevo-2026' → 'proyecto' es genérico, no un identificador único).
                    GENERIC_WORDS = {
                        "proyecto", "new", "nuevo", "demo", "test", "app", "web", "api",
                        "dev", "prod", "staging", "beta", "alpha", "site", "page",
                        "service", "servicio", "system", "sistema", "platform", "plataforma",
                    }
                    parent_dir = os.path.dirname(project_memory_dir)
                    if os.path.exists(parent_dir):
                        other_slugs = [d for d in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, d)) and d != slug]
                        for other in other_slugs:
                            keywords = [other, other.replace("-", " "), other.replace("-", "")]
                            parts = other.split("-")
                            # Solo agregar partes del slug que sean únicas (no genéricas, más de 3 chars)
                            meaningful_parts = [
                                p for p in parts
                                if len(p) > 3 and p.lower() not in GENERIC_WORDS
                            ]
                            if meaningful_parts:
                                keywords.append(meaningful_parts[0])
                            
                            for kw in keywords:
                                if len(kw) > 3 and kw.lower() not in GENERIC_WORDS and kw.lower() in content.lower():
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

    def validate_build(self) -> bool:
        """Valida que el comando de build (si existe) se ejecute correctamente."""
        pt = self.detect_project_type()
        if not pt:
            return True
            
        build_cmd = pt.get("herramienta_build")
        if not build_cmd:
            return True
            
        logger.info(f"Validando build del proyecto con comando: {build_cmd}")
        
        req_files = pt.get("archivos_requeridos", [])
        build_cwd = self.project_path
        
        if "package.json" in req_files:
            if not os.path.exists(os.path.join(self.project_path, "package.json")):
                for root, _, files in os.walk(self.project_path):
                    if "package.json" in files:
                        build_cwd = root
                        break
                        
        package_json_path = os.path.join(build_cwd, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, "r", encoding="utf-8") as f:
                    pj = json.load(f)
                if "build" not in pj.get("scripts", {}):
                    logger.info("package.json no tiene script de 'build'. Saltando validación de build.")
                    return True
            except Exception:
                pass

        import subprocess
        if os.path.exists(package_json_path):
            logger.info(f"Instalando dependencias (npm install) en {build_cwd}...")
            try:
                subprocess.run(
                    "npm install",
                    shell=True,
                    cwd=build_cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120
                )
            except Exception as e:
                logger.warning(f"Advertencia en npm install: {e}")
                
        try:
            res = subprocess.run(
                build_cmd,
                shell=True,
                cwd=build_cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120
            )
            if res.returncode != 0:
                self.errors.append(
                    f"BUILD_FAILED: El comando '{build_cmd}' falló en '{build_cwd}'. "
                    f"stdout: {res.stdout[:500]}... stderr: {res.stderr[:500]}..."
                )
                return False
            logger.info("Build del proyecto completado exitosamente.")
            
            # --- Validar esquema de base de datos Supabase si aplica ---
            # Si el proyecto tiene un package.json y usa Supabase o si es e-commerce
            is_ecommerce = "ecommerce" in self.project_path.lower()
            supabase_url = os.getenv("SUPABASE_URL", "")
            supabase_db_url = os.getenv("SUPABASE_DB_URL", "")
            if (is_ecommerce or supabase_url) and supabase_db_url:
                logger.info("Validando tablas requeridas en base de datos Supabase...")
                expected_tables = ["profiles", "categories", "products", "orders", "order_items"]
                try:
                    import pg8000
                except ImportError:
                    logger.info("Instalando pg8000 dinámicamente para validación de base de datos...")
                    import subprocess as sp
                    sp.run("pip install pg8000", shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
                    import pg8000
                
                try:
                    # Conectar a Supabase PostgreSQL via connection string
                    # Ej: postgresql://postgres:password@db.tu_proyecto.supabase.co:5432/postgres
                    url_clean = supabase_db_url.replace("postgresql://", "")
                    creds, host_port_db = url_clean.split("@")
                    user, password = creds.split(":")
                    host_port, db = host_port_db.split("/")
                    if ":" in host_port:
                        host, port = host_port.split(":")
                        port = int(port)
                    else:
                        host = host_port
                        port = 5432
                        
                    conn = pg8000.connect(user=user, password=password, host=host, port=port, database=db, timeout=10)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
                    )
                    existing_tables = [row[0] for row in cursor.fetchall()]
                    cursor.close()
                    conn.close()
                    
                    missing_tables = [t for t in expected_tables if t not in existing_tables]
                    if missing_tables:
                        self.errors.append(
                            f"DATABASE_VALIDATION_FAILED: Faltan las siguientes tablas requeridas en Supabase: {', '.join(missing_tables)}"
                        )
                        return False
                    logger.info("Validación de base de datos exitosa: Todas las tablas requeridas están presentes.")
                except Exception as db_err:
                    # Si falla por credenciales o timeout
                    self.errors.append(f"DATABASE_CONNECTION_ERROR: No se pudo conectar a Supabase para validar las tablas: {str(db_err)}")
                    return False

            return True
        except Exception as e:
            self.errors.append(f"BUILD_ERROR: Fallo al ejecutar el build '{build_cmd}': {str(e)}")
            return False

    def run(self) -> Dict:
        syntax = self.validate_syntax()
        structure = self.validate_structure()
        build_ok = self.validate_build()
        
        approved = (syntax and structure and build_ok)
        score = 10.0 if approved else max(2.0, 10.0 - (len(self.errors) * 2.0))
        
        reasons = []
        recommendations = []
        if not approved:
            reasons = [f"Fallo de control de calidad: {err}" for err in self.errors]
            recommendations = [
                "Corrija los errores de sintaxis indicados." if not syntax else "",
                "Asegúrese de incluir README.md y requirements.txt en la raíz del proyecto o solucione el build." if not (structure and build_ok) else ""
            ]
            recommendations = [r for r in recommendations if r]
        else:
            reasons = ["Todos los chequeos de calidad pasaron exitosamente."]
            recommendations = ["El proyecto mantiene los estándares de robustez 10/10."]

        decision = GateDecisionSchema(
            approved=approved,
            score=score,
            reasons=reasons,
            recommendations=recommendations
        )

        res = decision.model_dump()
        res["status"] = "SUCCESS" if approved else "FAIL"
        res["errors"] = self.errors
        res["checks"] = {
            "syntax": "OK" if syntax else "FAIL",
            "structure": "OK" if structure else "FAIL",
            "build": "OK" if build_ok else "FAIL"
        }
        return res


if __name__ == "__main__":
    # Prueba rápida
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    gate = QualityGate(path)
    print(gate.run())
