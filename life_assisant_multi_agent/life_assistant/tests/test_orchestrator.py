import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from orchestrator import orchestrate
from utils.file_utils import write_json, read_json

QUEUE_PATH = "messages/queue.json"

def test_orchestrator_marks_done(monkeypatch):
    # Préparer un message pour task_agent
    write_json(QUEUE_PATH, {"messages": [{"type": "test", "target": "task_agent", "payload": {"action": "create", "id": "t2", "data": {"title": "Test", "due_date": "2099-01-01T00:00:00"}}, "status": "new"}]})
    # Monkeypatch pour sortir après un tour
    monkeypatch.setattr("orchestrator.all_tasks_done", lambda: True)
    orchestrate()
    queue = read_json(QUEUE_PATH)
    assert queue["messages"][0]["status"] == "done"
