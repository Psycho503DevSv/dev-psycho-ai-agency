import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../runtime')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config import settings
from memory_engine import MemoryEngine
from graphiti_bridge import GraphitiBridge

class TestGraphitiMemory(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for memory engine file storage
        self.test_dir = tempfile.mkdtemp()
        self.engine = MemoryEngine(base_path=self.test_dir)

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_settings_load(self):
        # Verify settings exists
        self.assertTrue(hasattr(settings, 'USE_GRAPHITI'))
        self.assertTrue(hasattr(settings, 'NEO4J_URI'))
        self.assertTrue(hasattr(settings, 'NEO4J_USER'))
        self.assertTrue(hasattr(settings, 'NEO4J_PASSWORD'))

    def test_graphiti_disabled_by_default(self):
        # Unless explicitly set, USE_GRAPHITI is False or we mock it
        bridge = GraphitiBridge()
        self.assertFalse(bridge._initialized)
        
    @patch('runtime.graphiti_bridge.GraphitiBridge.initialize')
    def test_fallback_behavior_when_disabled(self, mock_init):
        # Ensure that if Graphiti is disabled, MemoryEngine still saves files correctly
        mock_init.return_value = False
        
        session_id = "test-session-fallback"
        data = {"action": "testing_fallback", "value": "check"}
        
        # Save memory
        file_path = self.engine.save_memory(session_id, data)
        self.assertTrue(os.path.exists(file_path))
        
        # Retrieve and verify
        retrieved = self.engine.retrieve_memory(session_id)
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0]["data"]["action"], "testing_fallback")

    @patch('runtime.graphiti_bridge.bridge.add_episode')
    @patch('runtime.graphiti_bridge.bridge.initialize')
    def test_graphiti_save_triggered_when_enabled(self, mock_init, mock_add_episode):
        # Enable Graphiti mock-wise and verify save calls add_episode
        mock_init.return_value = True
        mock_add_episode.return_value = True
        
        with patch('config.settings.USE_GRAPHITI', True):
            # We mock initialize to true
            from runtime.graphiti_bridge import bridge
            bridge._initialized = True
            bridge.enabled = True
            
            session_id = "test-session-active"
            data = {"action": "testing_graph", "value": "check"}
            
            self.engine.save_memory(session_id, data)
            
            # Since create_task is called, let's wait a small amount for async queue if loop runs,
            # or mock check. Since we might run in thread/sync context:
            self.assertTrue(mock_add_episode.called)

if __name__ == "__main__":
    unittest.main()
