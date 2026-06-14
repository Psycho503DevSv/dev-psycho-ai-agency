import os
import json
import logging
from datetime import datetime
try:
    from config import settings
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import settings

logger = logging.getLogger("AutoLearner")

class AutoLearner:
    def __init__(self):
        self.lessons_file = os.path.exists(os.path.join(settings.MEMORY_DIR, "lessons_learned.md"))
        self.lessons_path = os.path.join(settings.MEMORY_DIR, "lessons_learned.md")

    def _get_session_logs(self, session_id: str) -> list:
        """Recupera los logs JSON de la sesión actual."""
        session_dir = os.path.join(settings.SESSIONS_DIR, session_id)
        logs = []
        if os.path.exists(session_dir):
            for file in os.listdir(session_dir):
                if file.endswith(".json"):
                    file_path = os.path.join(session_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as f:
                            logs.append(json.load(f))
                    except Exception as e:
                        logger.warning(f"No se pudo leer log {file}: {str(e)}")
        return logs

    def extract_and_learn(self, session_id: str, workflow_id: str, status: str, quality_errors: list = None) -> bool:
        """Extrae lecciones de los logs de sesión e intenta actualizar lessons_learned.md."""
        logs = self._get_session_logs(session_id)
        if not logs and not quality_errors:
            logger.info("No hay logs o errores en la sesión para extraer lecciones.")
            return False

        # 1. Intentar usar NVIDIA NIM o OpenAI si las API Keys están configuradas
        nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
        openai_key = settings.OPENAI_API_KEY
        
        if nvidia_key or openai_key:
            try:
                import requests
                
                if nvidia_key:
                    logger.info("Utilizando NVIDIA NIM (gratuito) para extraer lecciones de la sesión...")
                    api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
                    api_key = nvidia_key
                    model_name = "meta/llama-3.1-8b-instruct"
                else:
                    logger.info("Utilizando OpenAI para extraer lecciones de la sesión...")
                    api_url = "https://api.openai.com/v1/chat/completions"
                    api_key = openai_key
                    model_name = "gpt-4o-mini"
                
                prompt = (
                    "Analiza los siguientes logs de sesión y errores del validador de calidad para extraer lecciones aprendidas de desarrollo de software.\n"
                    "Crea recomendaciones concisas en español para evitar que los agentes cometan los mismos errores en el futuro.\n\n"
                    f"Workflow: {workflow_id}\n"
                    f"Status Final: {status}\n"
                    f"Errores de QualityGate: {json.dumps(quality_errors, ensure_ascii=False)}\n"
                    f"Logs de la sesión:\n{json.dumps(logs, ensure_ascii=False, indent=2)}\n\n"
                    "Responde únicamente con una lista en formato markdown de las nuevas lecciones extraídas (máximo 3 bullets, muy concisos)."
                )
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "Eres el Agente Evaluador de AI DevOS, encargado de documentar lecciones aprendidas y errores técnicos."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.3
                }
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                res_data = response.json()
                new_lessons = res_data["choices"][0]["message"]["content"].strip()
                self._append_lessons(new_lessons)
                return True
            except Exception as e:
                logger.error(f"Error llamando al proveedor de LLM (HTTP) para aprendizaje automático: {str(e)}. Usando fallback local...")

        # 2. Heurística Local (Offline Fallback)
        logger.info("Ejecutando extractor heurístico local para autoaprendizaje...")
        heuristics = []
        
        # Analizar errores del Quality Gate
        if quality_errors:
            for err in quality_errors:
                if "SYNTAX_ERROR" in err:
                    heuristics.append(f"- **Sintaxis Correcta:** Validar la sintaxis de todos los archivos antes de dar por completado un cambio. Error reportado: `{err}`.")
                elif "MISSING_FILE" in err:
                    heuristics.append(f"- **Estructura Requerida:** Asegurar que los archivos obligatorios (`README.md`, `requirements.txt`) existan antes de la entrega final. Error: `{err}`.")
                else:
                    heuristics.append(f"- **Calidad y Estilo:** Cumplir con los estándares de control de calidad. Error reportado: `{err}`.")

        # Analizar fallos generales del workflow
        if status == "FAILED" and not heuristics:
            heuristics.append(f"- **Ejecución de Flujo:** El workflow `{workflow_id}` falló durante su ejecución. Validar dependencias y que el entorno de runtime local esté configurado correctamente.")

        if heuristics:
            new_lessons = "\n".join(heuristics)
            self._append_lessons(new_lessons)
            return True
        
        logger.info("No se encontraron fallos o anomalías en la sesión para aprender de forma heurística.")
        return False

    def _append_lessons(self, new_lessons_md: str):
        """Añade lecciones aprendidas de forma segura a memory/lessons_learned.md."""
        os.makedirs(os.path.dirname(self.lessons_path), exist_ok=True)
        
        existing_content = ""
        if os.path.exists(self.lessons_path):
            try:
                with open(self.lessons_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read().strip()
            except Exception as e:
                logger.warning(f"No se pudo leer lessons_learned.md existente: {str(e)}")

        if not existing_content:
            existing_content = "# Lessons Learned & Optimization History\n\n## System Wide Lessons"

        # Validar duplicados básicos
        lines_to_add = []
        for line in new_lessons_md.strip().split("\n"):
            clean_line = line.strip()
            if clean_line and clean_line not in existing_content:
                lines_to_add.append(line)

        if not lines_to_add:
            logger.info("Las lecciones detectadas ya están documentadas en lessons_learned.md. Saltando escritura.")
            return

        updated_content = existing_content + "\n" + "\n".join(lines_to_add) + "\n"
        
        try:
            with open(self.lessons_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            logger.info("Archivo memory/lessons_learned.md actualizado exitosamente con nuevas lecciones.")
        except Exception as e:
            logger.error(f"Error escribiendo en lessons_learned.md: {str(e)}")

if __name__ == "__main__":
    # Prueba del módulo
    learner = AutoLearner()
    learner.extract_and_learn("test_session_001", "wf-discovery", "FAILED", ["SYNTAX_ERROR: app.py - invalid syntax (L12)"])
