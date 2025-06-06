import time
import json
from utils.file_utils import read_json, write_json
from utils.llm_utils import run_llm

QUEUE_PATH = "messages/queue.json"
TASKS_PATH = "tasks.md"

def handle_task(msg):
    print(f"[Orchestrator] Dispatching to task_agent: {msg}")
    import task_agent
    task_agent.handle(msg["payload"])

def handle_calendar(msg):
    print(f"[Orchestrator] Dispatching to calendar_agent: {msg}")
    import calendar_agent
    calendar_agent.handle(msg["payload"])

def handle_health(msg):
    print(f"[Orchestrator] Dispatching to health_agent: {msg}")
    import health_agent
    health_agent.handle(msg["payload"])

def handle_memory(msg):
    print(f"[Orchestrator] Dispatching to memory_agent: {msg}")
    import memory_agent
    memory_agent.handle(msg["payload"])

def handle_code(msg):
    print(f"[Orchestrator] Dispatching to code_agent: {msg}")
    import code_agent
    code_agent.handle(msg["payload"])

def all_tasks_done():
    with open(TASKS_PATH, encoding="utf-8") as f:
        content = f.read()
    return "- [ ]" not in content

def orchestrate():
    print("[Orchestrator] Starting main loop...")
    while True:
        print("[Orchestrator] Reading queue...")
        queue = read_json(QUEUE_PATH)
        for message in queue.get("messages", []):
            print(f"[Orchestrator] Inspecting message: {message}")
            if message.get("status", "new") == "new":
                target = message.get("target")
                print(f"[Orchestrator] Handling target: {target}")
                if target == "task_agent":
                    handle_task(message)
                elif target == "calendar_agent":
                    handle_calendar(message)
                elif target == "health_agent":
                    handle_health(message)
                elif target == "memory_agent":
                    handle_memory(message)
                elif target == "code_agent":
                    handle_code(message)
                message["status"] = "done"
        write_json(QUEUE_PATH, queue)
        if all_tasks_done():
            print("[Orchestrator] All tasks done. Exiting loop.")
            break
        time.sleep(1)

if __name__ == "__main__":
    orchestrate()
