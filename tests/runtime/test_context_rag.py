import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../runtime')))

from runtime.context_compressor import ContextCompressor
from runtime.rag_engine import RAGEngine

class TestContextAndRAG(unittest.TestCase):
    def setUp(self):
        self.temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../temp_test_rag'))
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Crear archivo simulado para RAG
        self.code_file = os.path.join(self.temp_dir, "test_script.py")
        with open(self.code_file, "w", encoding="utf-8") as f:
            f.write("def calculate_magic_number():\n    return 42\n")

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_rag_engine_search(self):
        engine = RAGEngine(self.temp_dir)
        results = engine.search("calculate_magic_number")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["path"], "test_script.py")
        self.assertIn("calculate_magic_number", results[0]["snippet"])

    def test_context_compressor_no_trigger_under_limit(self):
        # 10k tokens de límite, historial corto no debe comprimirse
        compressor = ContextCompressor(token_limit=10000)
        messages = [
            {"role": "system", "content": "system instructions"},
            {"role": "user", "content": "hi"}
        ]
        compressed = compressor.compress_history(messages)
        self.assertEqual(len(compressed), 2)
        self.assertEqual(compressed[1]["content"], "hi")

    def test_context_compressor_trigger_over_limit(self):
        # Límite muy bajo de 2 tokens (o caracteres equivalentes) para forzar compresión
        compressor = ContextCompressor(token_limit=2)
        
        # Mockear llamada de LLM interna del compresor para evitar llamadas a API reales
        from unittest.mock import patch
        with patch.object(ContextCompressor, "_call_llm_for_summary", return_value="Resumen mockeado de la sesion"):
            messages = [
                {"role": "system", "content": "system instructions"},
                {"role": "user", "content": "hi agent, please edit code"},
                {"role": "assistant", "content": "sure, i wrote class Foo"},
                {"role": "user", "content": "run command"}
            ]
            compressed = compressor.compress_history(messages)
            
            # Debe contener el sistema inicial, el primer user, el resumen mockeado e inyectado, y el último user intacto
            self.assertEqual(compressed[0]["role"], "system")
            self.assertEqual(compressed[1]["content"], "hi agent, please edit code")
            self.assertIn("Resumen mockeado de la sesion", compressed[2]["content"])
            self.assertEqual(compressed[3]["content"], "run command")

if __name__ == "__main__":
    unittest.main()
