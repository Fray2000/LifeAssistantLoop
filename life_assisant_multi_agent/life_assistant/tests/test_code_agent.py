import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from code_agent import generate_code, modify_code, delete_code, run_code

CODE_WORKSPACE = "workspace/"


def test_generate_modify_delete_run_code():
    payload = {"data": {"spec": "print('Bonjour, monde')", "filename": "hello.py"}}
    path = generate_code(payload)
    assert os.path.exists(path)
    modify_code({"data": {"filename": "hello.py", "old": "Bonjour", "new": "Salut"}})
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Salut, monde" in content
    output = run_code({"data": {"filename": "hello.py"}})
    assert "Salut, monde" in output or "Bonjour, monde" in output
    delete_code({"data": {"filename": "hello.py"}})
    assert not os.path.exists(path)
