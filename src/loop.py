import time
import json
import os
from .thinker import Thinker
from .editor import Editor
from .function_executor import FunctionExecutor
from .utils import read_file, write_file, log_change, log_self_review

PLAN = os.path.join(os.path.dirname(__file__), 'plan.md')
TASKS = os.path.join(os.path.dirname(__file__), 'tasks.md')
CRON = os.path.join(os.path.dirname(__file__), 'cron.md')
HUMAN_INPUT = os.path.join(os.path.dirname(__file__), 'human_input.md')
MEMORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'memory.json')
CHANGE_LOG = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'change_log.md')
SELF_REVIEW = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'self_review.md')

class LifeAssistantLoop:
    def __init__(self):
        self.thinker = Thinker()
        self.editor = Editor()
        self.executor = FunctionExecutor()
        self.memory = self.load_memory()

    def load_memory(self):
        try:
            with open(MEMORY, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def save_memory(self):
        with open(MEMORY, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def run(self):
        while True:
            # Reload memory at each loop
            self.memory = self.load_memory()
            # 1. Read plan, tasks, cron
            plan = read_file(PLAN)
            tasks = read_file(TASKS)
            cron = read_file(CRON)
            # 2. Check for human input
            human_input = read_file(HUMAN_INPUT)
            # 3. Reason and decide next actions
            prompt = self.thinker.build_prompt('', plan, tasks, cron, human_input, self.memory)
            print("\n-------------- PROMPT --------------\n" + prompt)
            thoughts, actions = self.thinker.reason(
                '', plan, tasks, cron, human_input, self.memory
            )
            print("\n-------------- ANSWER --------------\n")
            print("===== MODEL THOUGHTS =====\n" + thoughts)
            print("\n===== MODEL ACTIONS =====\n" + json.dumps(actions, indent=2))
            # 4. Execute actions
            for action in actions:
                result = self.executor.execute(action, self.editor, self.memory)
                log_change(CHANGE_LOG, action, result)
            # 5. Save memory
            self.save_memory()
            # 6. Self-reflection
            log_self_review(SELF_REVIEW, thoughts)
            # 7. Wait or break if paused
            if 'pause' in (human_input or '').lower():
                break
            time.sleep(5)

if __name__ == '__main__':
    loop = LifeAssistantLoop()
    loop.run()
