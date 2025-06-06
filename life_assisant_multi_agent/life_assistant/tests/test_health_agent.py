import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from health_agent import update_medical, set_reminder
from utils.file_utils import write_json, read_json

MEDICAL_PATH = "memory/medical.json"

def test_update_medical():
    write_json(MEDICAL_PATH, [])
    payload = {"id": "m1", "data": {"type": "medication", "details": "Lisinopril 10mg"}}
    update_medical(payload)
    data = read_json(MEDICAL_PATH)
    assert any(e["id"] == "m1" for e in data)
