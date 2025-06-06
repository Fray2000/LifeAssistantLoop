import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from utils.file_utils import write_json, read_json
from task_agent import create_task, update_task, delete_task

TEST_PATH = "memory/tasks.json"

def test_create_update_delete_task():
    # Nettoyage
    write_json(TEST_PATH, [])
    payload = {"id": "t1", "data": {"title": "Test", "due_date": "2099-01-01T00:00:00"}}
    create_task(payload)
    tasks = read_json(TEST_PATH)
    assert any(t["id"] == "t1" for t in tasks)
    update_task({"id": "t1", "data": {"title": "Test2"}})
    tasks = read_json(TEST_PATH)
    assert any(t["title"] == "Test2" for t in tasks)
    delete_task({"id": "t1"})
    tasks = read_json(TEST_PATH)
    assert not any(t["id"] == "t1" for t in tasks)
