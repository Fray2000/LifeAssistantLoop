import datetime

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
    with open(change_log_path, 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] Action: {action}, Result: {result}\n")

def log_self_review(self_review_path, thoughts):
    with open(self_review_path, 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {thoughts}\n")
