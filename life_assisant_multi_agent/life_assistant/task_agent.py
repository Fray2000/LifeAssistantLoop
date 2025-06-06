import datetime
from utils.file_utils import read_json, write_json
import schedule
import threading
import time
from utils.llm_utils import run_llm

TASK_PATH = "memory/tasks.json"
QUEUE_PATH = "messages/queue.json"

def create_task(payload: dict) -> None:
    tasks = read_json(TASK_PATH)
    if not isinstance(tasks, list):
        tasks = []
    new_task = {
        "id": payload["id"],
        "title": payload["data"]["title"],
        "due_date": payload["data"]["due_date"],
        "status": "new"
    }
    tasks.append(new_task)
    write_json(TASK_PATH, tasks)

def update_task(payload: dict) -> None:
    tasks = read_json(TASK_PATH)
    for t in tasks:
        if t["id"] == payload["id"]:
            t.update(payload["data"])
    write_json(TASK_PATH, tasks)

def delete_task(payload: dict) -> None:
    tasks = [t for t in read_json(TASK_PATH) if t["id"] != payload["id"]]
    write_json(TASK_PATH, tasks)

def send_reminder(task):
    queue = read_json(QUEUE_PATH)
    queue.setdefault("messages", []).append({
        "type": "reminder",
        "target": "interface_agent",
        "payload": {"task_id": task["id"], "title": task["title"]},
        "status": "new"
    })
    write_json(QUEUE_PATH, queue)

def schedule_reminders():
    def check_tasks():
        tasks = read_json(TASK_PATH)
        now = datetime.datetime.now()
        for task in tasks:
            if task["status"] != "done":
                due = datetime.datetime.fromisoformat(task["due_date"])
                if 0 <= (due - now).total_seconds() < 60:
                    send_reminder(task)
    schedule.every(30).seconds.do(check_tasks)
    while True:
        schedule.run_pending()
        time.sleep(1)

def handle(payload):
    print(f"[TaskAgent] handle() called with payload: {payload}")
    action = payload.get("action")
    if action == "create":
        print("[TaskAgent] Action: create")
        create_task(payload)
    elif action == "update":
        print("[TaskAgent] Action: update")
        update_task(payload)
    elif action == "delete":
        print("[TaskAgent] Action: delete")
        delete_task(payload)
    elif action == "natural_language":
        print("[TaskAgent] Action: natural_language")
        user_text = payload.get("text", "")
        response = run_llm(user_text, model_name="mistral", agent="task_agent", function="natural_language")
        queue = read_json(QUEUE_PATH)
        queue.setdefault("messages", []).append({
            "type": "assistant_message",
            "target": "interface_agent",
            "payload": {"message": response},
            "status": "new"
        })
        write_json(QUEUE_PATH, queue)
        print("[TaskAgent] Wrote assistant_message to queue.")
    else:
        print(f"[TaskAgent] Unknown action: {action}")

# Lancement du scheduler en thread séparé
threading.Thread(target=schedule_reminders, daemon=True).start()
