import requests
import os
from datetime import datetime
import json

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "model_debug.log")

def log_llm_event(event_type, prompt, response=None, model=None, agent=None, function=None, error=None, extra=None):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "model": model,
        "agent": agent,
        "function": function,
        "prompt": prompt,
        "response": response,
        "error": error,
        "extra": extra
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def run_llm(prompt: str, model_name: str, agent=None, function=None) -> str:
    """Appelle toujours le modèle Mistral d'Ollama local pour toute génération LLM (hors embeddings)."""
    model = "mistral"
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    log_llm_event("llm_request", prompt, model=model, agent=agent, function=function)
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json().get("response", "")
        log_llm_event("llm_response", prompt, response=result, model=model, agent=agent, function=function)
        return result
    except Exception as e:
        log_llm_event("llm_error", prompt, response=None, model=model, agent=agent, function=function, error=str(e))
        print(f"[LLM ERROR] {e}")  # <--- Added for debug
        return ""

# Test rapide (désactivé par défaut)
if __name__ == "__main__":
    print(run_llm("print('test')", "mistral-7b", agent="test", function="main"))
