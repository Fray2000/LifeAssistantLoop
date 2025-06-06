import json
import time
from utils.file_utils import read_json, write_json

QUEUE_PATH = "messages/queue.json"

# Agent d'interface : point d'entrée pour afficher les messages à l'utilisateur ou recevoir des entrées utilisateur.
# (Stub, à compléter selon l'UI choisie)

def handle(payload):
    print(f"[INTERFACE AGENT] Message reçu: {payload}")
    # Optionally, format and print only the message for chat
    if isinstance(payload, dict) and "message" in payload:
        print(f"Assistant: {payload['message']}")

# Simple CLI chat loop for natural language interaction with the orchestrator

def chat():
    print("[LifeAssistant] Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("exit", "quit"): break
        # Add user message to queue
        queue = read_json(QUEUE_PATH)
        queue.setdefault("messages", []).append({
            "type": "user_message",
            "target": "task_agent",  # Default to task_agent, can be improved
            "payload": {"action": "natural_language", "text": user_input},
            "status": "new"
        })
        write_json(QUEUE_PATH, queue)
        # Wait for a response from any agent (interface_agent preferred)
        print("[LifeAssistant] Waiting for response...")
        for _ in range(30):  # Wait up to 30 seconds
            queue = read_json(QUEUE_PATH)
            responses = [m for m in queue.get("messages", []) if m.get("target") == "interface_agent" and m.get("status") == "new"]
            if responses:
                for resp in responses:
                    print(f"Assistant: {resp.get('payload', {}).get('message', resp.get('payload'))}")
                    resp["status"] = "done"
                write_json(QUEUE_PATH, queue)
                break
            time.sleep(1)
        else:
            print("[LifeAssistant] No response received.")

if __name__ == "__main__":
    chat()
