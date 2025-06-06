import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from utils.file_utils import write_json, read_json
from memory_agent import update_memory, query_memory

PROFILE_PATH = "memory/profile.json"

def test_update_and_query_memory():
    write_json(PROFILE_PATH, [])
    update_memory({"data": {"text": "Utilisateur aime le cyclisme"}})
    results = query_memory({"data": {"query": "cyclisme"}})
    assert any("cyclisme" in r.get("text", "") for r in results)
