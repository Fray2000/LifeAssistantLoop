from utils.file_utils import read_json, write_json
import datetime
import schedule
import threading
import time

MEDICAL_PATH = "memory/medical.json"
QUEUE_PATH = "messages/queue.json"

def update_medical(payload: dict) -> None:
    data = read_json(MEDICAL_PATH)
    if not isinstance(data, list):
        data = []
    entry = {
        "id": payload["id"],
        "type": payload["data"].get("type", "medication"),
        "details": payload["data"]["details"],
        "timestamp": datetime.datetime.now().isoformat()
    }
    data.append(entry)
    write_json(MEDICAL_PATH, data)

def send_health_reminder(entry):
    queue = read_json(QUEUE_PATH)
    queue.setdefault("messages", []).append({
        "type": "health_reminder",
        "target": "interface_agent",
        "payload": {"entry_id": entry["id"], "details": entry["details"]},
        "status": "new"
    })
    write_json(QUEUE_PATH, queue)

def set_reminder(payload: dict) -> None:
    freq = payload["data"].get("frequency", "daily")
    hour = payload["data"].get("hour", 8)
    def job():
        send_health_reminder(payload)
    if freq == "daily":
        schedule.every().day.at(f"{hour:02d}:00").do(job)
    elif freq == "weekly":
        schedule.every().monday.at(f"{hour:02d}:00").do(job)

def handle(payload):
    if payload.get("action") == "update_medical":
        update_medical(payload)
    elif payload.get("action") == "set_reminder":
        set_reminder(payload)

threading.Thread(target=lambda: (schedule.run_pending() or time.sleep(1)), daemon=True).start()
