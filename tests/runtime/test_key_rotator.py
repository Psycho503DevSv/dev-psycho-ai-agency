import os
import tempfile
import json
import pytest
from unittest.mock import patch
from datetime import date

from runtime.key_rotator import (
    parse_keys,
    get_active_key,
    mark_key_exhausted,
    is_quota_error,
    is_permanent_error,
    get_rotation_status,
    get_valid_keys,
    _STATE_FILE
)

@pytest.fixture(autouse=True)
def temp_state_file():
    """Fixture to redirect key rotator state to a temporary file during tests."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        temp_path = tmp.name
    
    # Pre-populate the state to avoid rotation on first run
    initial_state = {
        "gemini": {
            "last_rotation_date": str(date.today()),
            "base_index": 0,
            "exhausted_today": [],
            "permanently_invalid": []
        }
    }
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(initial_state, f)

    # Patch the state file path in key_rotator
    with patch("runtime.key_rotator._STATE_FILE", temp_path):
        yield temp_path
        
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass

def test_parse_keys():
    assert parse_keys("key1,key2 , key3") == ["key1", "key2", "key3"]
    assert parse_keys("") == []
    assert parse_keys(None) == []

def test_is_quota_error():
    assert is_quota_error(429, "") is True
    assert is_quota_error(503, "") is True
    assert is_quota_error(200, "rate limit exceeded") is True
    assert is_quota_error(200, "normal response") is False

def test_is_permanent_error():
    assert is_permanent_error(403, "") is True
    assert is_permanent_error(200, "api key not valid") is True
    assert is_permanent_error(200, "invalid api key") is True
    assert is_permanent_error(200, "normal response") is False

def test_get_active_key_and_rotation(temp_state_file):
    keys = ["k1", "k2", "k3"]
    
    # First active key should be k1 since we initialized the state date to today
    k = get_active_key("gemini", keys)
    assert k == "k1"
    
    # Mark k1 exhausted (quota)
    mark_key_exhausted("gemini", keys, "k1", permanent=False)
    k = get_active_key("gemini", keys)
    assert k == "k2"
    
    # Mark k2 permanently invalid (403)
    mark_key_exhausted("gemini", keys, "k2", permanent=True)
    k = get_active_key("gemini", keys)
    assert k == "k3"
    
    # Test valid keys helper
    valid_keys = get_valid_keys("gemini", keys)
    assert "k2" not in valid_keys
    assert "k1" in valid_keys  # k1 is only exhausted today, not permanently invalid
    assert "k3" in valid_keys

    # Test status
    status = get_rotation_status()
    assert "gemini" in status
    assert status["gemini"]["exhausted_today"] == 1
    
    # Exhaust all remaining valid keys (k1 is exhausted, k2 permanent, k3 now exhausted)
    mark_key_exhausted("gemini", keys, "k3", permanent=False)
    # Since all non-permanent keys are exhausted, it should reset the exhausted ones
    k = get_active_key("gemini", keys)
    assert k in ["k1", "k3"]
    assert k != "k2"  # permanently invalid key never returns

def test_all_keys_permanently_invalid(temp_state_file):
    keys = ["k1", "k2"]
    mark_key_exhausted("gemini", keys, "k1", permanent=True)
    mark_key_exhausted("gemini", keys, "k2", permanent=True)
    
    # Should return None because all are permanently invalid
    assert get_active_key("gemini", keys) is None
