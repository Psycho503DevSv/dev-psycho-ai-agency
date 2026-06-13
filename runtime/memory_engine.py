import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from config import settings

class MemoryEngine:
    def __init__(self, base_path: str = None):
        self.base_path = base_path or settings.MEMORY_DIR
        self.sessions_path = os.path.join(base_path, "sessions") if base_path else settings.SESSIONS_DIR
        self.patterns_path = os.path.join(base_path, "patterns") if base_path else settings.PATTERNS_DIR
        self._ensure_paths()

    def _ensure_paths(self):
        os.makedirs(self.sessions_path, exist_ok=True)
        os.makedirs(self.patterns_path, exist_ok=True)

    def save_memory(self, session_id: str, data: Dict, category: str = "logs") -> str:
        """Guarda un fragmento de memoria en la sesión activa."""
        target_dir = os.path.join(self.sessions_path, session_id)
        os.makedirs(target_dir, exist_ok=True)
        
        entry_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        file_path = os.path.join(target_dir, f"{category}_{entry_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "data": data
            }, f, indent=2)
        
        return file_path

    def retrieve_memory(self, session_id: str) -> List[Dict]:
        """Recupera toda la memoria de una sesión específica."""
        target_dir = os.path.join(self.sessions_path, session_id)
        if not os.path.exists(target_dir):
            return []
        
        memories = []
        for file in sorted(os.listdir(target_dir)):
            if file.endswith(".json"):
                with open(os.path.join(target_dir, file), 'r', encoding='utf-8-sig') as f:
                    memories.append(json.load(f))
        return memories

    def promote_memory(self, session_id: str, pattern_name: str, data: Dict):
        """Promueve un aprendizaje de sesión a patrón global."""
        file_path = os.path.join(self.patterns_path, f"{pattern_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "promoted_at": datetime.now().isoformat(),
                "source_session": session_id,
                "pattern": data
            }, f, indent=2)

    def search(self, query: str, session_id: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        """Busca registros en la memoria filtrando por texto en el contenido JSON."""
        results = []
        search_dirs = []
        if session_id:
            specific_dir = os.path.join(self.sessions_path, session_id)
            if os.path.exists(specific_dir):
                search_dirs.append(specific_dir)
        else:
            if os.path.exists(self.sessions_path):
                for d in os.listdir(self.sessions_path):
                    full_d = os.path.join(self.sessions_path, d)
                    if os.path.isdir(full_d):
                        search_dirs.append(full_d)
        
        if not session_id and os.path.exists(self.patterns_path):
            search_dirs.append(self.patterns_path)

        query_lower = query.lower()
        for directory in search_dirs:
            for file in os.listdir(directory):
                if file.endswith(".json"):
                    if category and not file.startswith(category):
                        continue
                    file_path = os.path.join(directory, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as f:
                            content = json.load(f)
                            content_str = json.dumps(content, ensure_ascii=False).lower()
                            if query_lower in content_str:
                                results.append(content)
                    except Exception:
                        pass
        return results

if __name__ == "__main__":
    engine = MemoryEngine()
    test_id = "test_session_001"
    path = engine.save_memory(test_id, {"event": "startup", "status": "ok"})
    print(f"Memoria guardada en: {path}")
    print(f"Items recuperados: {len(engine.retrieve_memory(test_id))}")
    print(f"Búsqueda 'startup': {len(engine.search('startup'))}")
