from utils.file_utils import read_json, write_json
from utils.memory_utils import add_to_memory, retrieve_from_memory

PROFILE_PATH = "memory/profile.json"
QUEUE_PATH = "messages/queue.json"

def update_memory(payload: dict) -> None:
    add_to_memory(payload["data"], PROFILE_PATH)

def query_memory(payload: dict) -> list:
    results = retrieve_from_memory(payload["data"]["query"])
    return results

def handle(payload):
    if payload.get("action") == "update_memory":
        update_memory(payload)
    elif payload.get("action") == "query_memory":
        results = query_memory(payload)
        queue = read_json(QUEUE_PATH)
        queue.setdefault("messages", []).append({
            "type": "memory_response",
            "target": "interface_agent",
            "payload": {"results": results},
            "status": "new"
        })
        write_json(QUEUE_PATH, queue)
