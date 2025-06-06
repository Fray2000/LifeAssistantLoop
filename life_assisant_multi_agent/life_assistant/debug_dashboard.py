import threading
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import json
import os
from utils.file_utils import read_json, write_json

QUEUE_PATH = os.path.join(os.path.dirname(__file__), "messages", "queue.json")
LOG_PATH = os.path.join(os.path.dirname(__file__), "logs", "model_debug.log")

# Ensure log file exists at startup
def ensure_log_file():
    log_dir = os.path.dirname(LOG_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("")

class DebugDashboard(tk.Tk):
    def __init__(self):
        ensure_log_file()
        super().__init__()
        self.title("LifeAssistant Debug Dashboard")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Status label for orchestrator
        self.status_var = tk.StringVar(value="[Status] Orchestrator: Starting...")
        self.status_label = tk.Label(self, textvariable=self.status_var, fg="blue")
        self.status_label.pack(fill=tk.X)

        self.log = ScrolledText(self, state="disabled", height=18)
        self.log.pack(fill=tk.BOTH, expand=True)

        self.model_log = ScrolledText(self, state="disabled", height=7, bg="#222", fg="#0f0")
        self.model_log.pack(fill=tk.BOTH, expand=False)
        self.model_log.insert(tk.END, "[Model Debug Log]\n")

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.user_entry = tk.Entry(self.input_frame)
        self.user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.user_entry.bind("<Return>", self.send_message)
        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=5)

        self.running = True
        self.last_seen = 0
        self.after(1000, self.poll_queue)
        self.after(1500, self.poll_model_log)
        self.after(500, self.check_orchestrator_status)

    def log_message(self, msg):
        self.log.config(state="normal")
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")

    def send_message(self, event=None):
        text = self.user_entry.get().strip()
        if not text:
            return
        queue = read_json(QUEUE_PATH)
        queue.setdefault("messages", []).append({
            "type": "user_message",
            "target": "task_agent",
            "payload": {"action": "natural_language", "text": text},
            "status": "new"
        })
        write_json(QUEUE_PATH, queue)
        self.log_message(f"[You] {text}")
        self.user_entry.delete(0, tk.END)

    def poll_queue(self):
        if not self.running:
            return
        try:
            queue = read_json(QUEUE_PATH)
            for msg in queue.get("messages", []):
                if msg.get("status") == "new" and msg.get("target") == "interface_agent":
                    payload = msg.get("payload", {})
                    if isinstance(payload, dict) and "message" in payload:
                        self.log_message(f"[Assistant] {payload['message']}")
                    else:
                        self.log_message(f"[Assistant] {payload}")
                    msg["status"] = "done"
            write_json(QUEUE_PATH, queue)
        except Exception as e:
            self.log_message(f"[Error] {e}")
        self.after(1000, self.poll_queue)

    def poll_model_log(self):
        try:
            log_path = os.path.join(os.path.dirname(__file__), "logs", "model_debug.log")
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[-20:]  # Show last 20 entries
                self.model_log.config(state="normal")
                self.model_log.delete(1.0, tk.END)
                if lines:
                    self.model_log.insert(tk.END, "".join(lines))
                else:
                    self.model_log.insert(tk.END, "[Model Debug Log is empty]\n")
                self.model_log.see(tk.END)
                self.model_log.config(state="disabled")
            else:
                self.model_log.config(state="normal")
                self.model_log.delete(1.0, tk.END)
                self.model_log.insert(tk.END, "[Model Debug Log not found]\n")
                self.model_log.config(state="disabled")
        except Exception as e:
            self.model_log.config(state="normal")
            self.model_log.insert(tk.END, f"[Error] {e}\n")
            self.model_log.config(state="disabled")
        self.after(1500, self.poll_model_log)

    def check_orchestrator_status(self):
        # Check if orchestrator thread is alive
        if hasattr(self, 'orch_thread') and not self.orch_thread.is_alive():
            self.status_var.set("[Status] Orchestrator: Error (thread stopped)")
            self.status_label.config(fg="red")
        else:
            self.status_var.set("[Status] Orchestrator: Running")
            self.status_label.config(fg="green")
        self.after(2000, self.check_orchestrator_status)

    def on_close(self):
        self.running = False
        self.destroy()

# Orchestrator runner (background)
def run_orchestrator(dashboard=None):
    try:
        import orchestrator
        if dashboard:
            dashboard.status_var.set("[Status] Orchestrator: Running")
            dashboard.status_label.config(fg="green")
        orchestrator.orchestrate()
    except Exception as e:
        if dashboard:
            dashboard.status_var.set(f"[Status] Orchestrator: Error: {e}")
            dashboard.status_label.config(fg="red")
        print(f"[Orchestrator Error] {e}")

if __name__ == "__main__":
    app = DebugDashboard()
    # Start orchestrator in a background thread and pass dashboard for status updates
    app.orch_thread = threading.Thread(target=run_orchestrator, args=(app,), daemon=True)
    app.orch_thread.start()
    app.mainloop()
