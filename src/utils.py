import datetime
import json
import os

def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception:
        return ''

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def log_change(change_log_path, action, result):
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(change_log_path), exist_ok=True)
    with open(change_log_path, 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] Action: {action}, Result: {result}\n")

def log_self_review(self_review_path, thoughts):
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(self_review_path), exist_ok=True)
    with open(self_review_path, 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {thoughts}\n")
        
def log_perception_action(log_path, perception_data, actions_data):
    """
    Log what the agent perceives and what actions it takes
    
    Args:
        log_path: Path to the log file
        perception_data: Dictionary containing what the agent perceives (plan, tasks, cron, human_input)
        actions_data: List of actions the agent takes
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Format the perception data for logging
    perception_summary = {
        "plan": perception_data.get("plan", "")[:100] + "..." if perception_data.get("plan") else "",
        "tasks": perception_data.get("tasks", "")[:100] + "..." if perception_data.get("tasks") else "",
        "cron": perception_data.get("cron", "")[:100] + "..." if perception_data.get("cron") else "",
        "human_input": perception_data.get("human_input", "")[:100] + "..." if perception_data.get("human_input") else "",
        "memory_keys": list(perception_data.get("memory", {}).keys())
    }
    
    with open(log_path, 'a') as f:
        f.write(f"\n[{datetime.datetime.now().isoformat()}] === AGENT CYCLE ===\n")
        f.write(f"PERCEPTION:\n{json.dumps(perception_summary, indent=2)}\n\n")
        f.write(f"ACTIONS:\n{json.dumps(actions_data, indent=2)}\n")
        f.write("="*50 + "\n")
