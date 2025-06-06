import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from calendar_agent import create_event, detect_conflicts

# Ces tests nécessitent un mock de l'API Google Calendar ou un environnement de test dédié.

def test_create_event(monkeypatch):
    class DummyService:
        def events(self):
            class DummyEvents:
                def insert(self, calendarId, body):
                    class DummyExec:
                        def execute(self):
                            return {"id": "evt1"}
                    return DummyExec()
            return DummyEvents()
    monkeypatch.setattr("calendar_agent.get_service", lambda: DummyService())
    payload = {"data": {"summary": "Test", "start": "2099-01-01T00:00:00", "end": "2099-01-01T01:00:00", "attendees": []}}
    eid = create_event(payload)
    assert eid == "evt1"

def test_detect_conflicts(monkeypatch):
    class DummyService:
        def freebusy(self):
            class DummyFreeBusy:
                def query(self, body):
                    class DummyExec:
                        def execute(self):
                            return {"calendars": {"primary": {"busy": []}}}
                    return DummyExec()
            return DummyFreeBusy()
    monkeypatch.setattr("calendar_agent.get_service", lambda: DummyService())
    payload = {"data": {"start": "2099-01-01T00:00:00", "end": "2099-01-01T01:00:00"}}
    assert detect_conflicts(payload)
