#!/usr/bin/env python3

import time
import json
import os
import datetime
import requests
import sys

# Direct imports (no relative imports)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.thinker import Thinker
from src.editor import Editor
from src.function_executor import FunctionExecutor
from src.utils import read_file, write_file, log_change, log_self_review

# Path definitions
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'src')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

PLAN = os.path.join(SRC_DIR, 'plan.md')
TASKS = os.path.join(SRC_DIR, 'tasks.md')
CRON = os.path.join(SRC_DIR, 'cron.md')
HUMAN_INPUT = os.path.join(SRC_DIR, 'human_input.md')
MEMORY = os.path.join(DATA_DIR, 'memory.json')
CHANGE_LOG = os.path.join(LOGS_DIR, 'change_log.md')
SELF_REVIEW = os.path.join(LOGS_DIR, 'self_review.md')

class LifeAssistantLoop:
    def __init__(self):
        print("Initializing Life Assistant Agent...")
        self.thinker = Thinker()
        self.editor = Editor()
        self.executor = FunctionExecutor()
        self.memory = self.load_memory()
        # Update startup time in memory
        self.memory.setdefault('system', {})['last_startup'] = datetime.datetime.now().isoformat()
        self.memory.setdefault('system', {})['cycles_completed'] = self.memory.get('system', {}).get('cycles_completed', 0)
        self.save_memory()
        print(f"Memory loaded with {len(self.memory)} keys")

    def load_memory(self):
        try:
            with open(MEMORY, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
            return {}

    def save_memory(self):
        try:
            with open(MEMORY, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def run(self):
        print("Starting Life Assistant main loop...")
        while True:
            try:
                print("\n" + "="*50)
                print(f"CYCLE {self.memory.get('system', {}).get('cycles_completed', 0) + 1}")
                print("="*50)
                
                # Reload memory at each loop
                self.memory = self.load_memory()
                
                # 1. Read plan, tasks, cron
                plan = read_file(PLAN)
                tasks = read_file(TASKS)
                cron = read_file(CRON)
                
                # 2. Check for human input
                human_input = read_file(HUMAN_INPUT)
                if human_input:
                    print(f"Human input detected: {human_input[:100]}...")
                    # Update last human interaction time
                    self.memory.setdefault('system', {})['last_human_interaction'] = datetime.datetime.now().isoformat()
                
                # 3. Reason and decide next actions
                print("Thinking about next actions...")
                prompt = self.thinker.build_prompt('', plan, tasks, cron, human_input, self.memory)
                print("\n-------------- PROMPT --------------\n" + prompt)
                
                try:
                    thoughts, actions = self.thinker.reason(
                        '', plan, tasks, cron, human_input, self.memory
                    )
                except Exception as e:
                    print(f"Error during reasoning: {e}")
                    thoughts = f"Error occurred: {e}"
                    actions = []
                
                print("\n-------------- ANSWER --------------\n")
                print("===== MODEL THOUGHTS =====\n" + thoughts)
                print("\n===== MODEL ACTIONS =====\n" + json.dumps(actions, indent=2))
                
                # 4. Execute actions
                for i, action in enumerate(actions):
                    try:
                        print(f"Executing action {i+1}/{len(actions)}: {action.get('type')}")
                        result = self.executor.execute(action, self.editor, self.memory)
                        log_change(CHANGE_LOG, action, result)
                        print(f"Result: {result}")
                    except Exception as e:
                        error_msg = f"Error executing action {action.get('type')}: {e}"
                        print(error_msg)
                        log_change(CHANGE_LOG, action, error_msg)

                # 5. Update cycle count in memory
                self.memory.setdefault('system', {})['cycles_completed'] = self.memory.get('system', {}).get('cycles_completed', 0) + 1
                
                # 6. Save memory
                self.save_memory()
                
                # 7. Self-reflection
                log_self_review(SELF_REVIEW, thoughts)
                
                # 8. Wait or break if paused
                if 'pause' in (human_input or '').lower():
                    print("Pause command detected. Stopping loop.")
                    break
                    
                # 9. Check if user wants to quit (e.g. Ctrl+C)
                time_to_wait = 5
                print(f"Waiting {time_to_wait} seconds before next cycle (Ctrl+C to exit)...")
                time.sleep(time_to_wait)
                
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected. Exiting gracefully.")
                break
            except Exception as e:
                print(f"Unexpected error in main loop: {e}")
                # Log the error but continue with the next cycle
                with open(os.path.join(LOGS_DIR, 'errors.log'), 'a') as f:
                    f.write(f"[{datetime.datetime.now().isoformat()}] Error: {str(e)}\n")
                time.sleep(5)  # Wait before retrying
        
        print("Life Assistant loop ended. Saving final state...")
        self.save_memory()
        print("Done.")

if __name__ == '__main__':
    loop = LifeAssistantLoop()
    loop.run()
