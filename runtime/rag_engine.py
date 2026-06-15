import os
import re
import fnmatch
from typing import List, Dict, Any

class RAGEngine:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.ignore_patterns = [
            ".git", "__pycache__", "*.pyc", ".pytest_cache", ".venv", "node_modules", "dist", "build", "*.png", "*.jpg", "*.apk"
        ]

    def _should_ignore(self, path: str) -> bool:
        """Determina si un archivo o directorio debe ser omitido en el índice."""
        parts = path.split(os.sep)
        for part in parts:
            if part.startswith("."):
                return True
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True
        return False

    def index_project(self) -> List[Dict[str, Any]]:
        """Recorre el workspace e indexa todos los archivos de código fuente legibles."""
        documents = []
        for root, dirs, files in os.walk(self.workspace_dir):
            # Filtrar directorios a ignorar in-place
            dirs[:] = [d for d in dirs if not self._should_ignore(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self._should_ignore(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Guardamos el archivo y metadatos básicos
                    documents.append({
                        "rel_path": os.path.relpath(file_path, self.workspace_dir),
                        "content": content,
                        "size": len(content)
                    })
                except Exception:
                    pass
        return documents

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Realiza una búsqueda basada en coincidencia de palabras clave y similitud de texto simple."""
        documents = self.index_project()
        if not documents or not query:
            return []

        # Tokenizar query
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return []

        scored_docs = []
        for doc in documents:
            content_lower = doc["content"].lower()
            score = 0
            
            # Coincidencia exacta de palabras clave en el contenido
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)
                if word in doc["rel_path"].lower():
                    score += 10 # Bonus por match en la ruta del archivo

            if score > 0:
                scored_docs.append((score, doc))

        # Ordenar por puntaje descendente
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                "path": doc["rel_path"],
                "score": score,
                # Retornar un fragmento representativo del archivo para ahorrar tokens
                "snippet": doc["content"][:2000] + ("\n... [TRUNCADO] ..." if len(doc["content"]) > 2000 else "")
            })
        return results
