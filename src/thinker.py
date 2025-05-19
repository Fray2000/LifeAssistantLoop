import requests
import json
from .utils import read_file, write_file

#OLLAMA_URL = 'http://umbrel.local:11434/api/generate'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'tinyllama'

class Thinker:
    def __init__(self):
        pass

    def reason(self, deployment_plan, plan, tasks, cron, human_input, memory):
        prompt = self.build_prompt(deployment_plan, plan, tasks, cron, human_input, memory)
        response = self.query_llm(prompt)
        thoughts, actions = self.parse_response(response)
        return thoughts, actions

    def build_prompt(self, deployment_plan, plan, tasks, cron, human_input, memory):
        return f"""
You are an autonomous life assistant agent with the ability to modify your own environment and improve yourself.

Project Plan:\n{plan}\n
Tasks:\n{tasks}\n
Cron:\n{cron}\n
Human Input:\n{human_input}\n
Memory:\n{json.dumps(memory)}\n

As an autonomous agent, you should:
1. Analyze the current state of tasks, cron jobs, and any human input
2. Maintain and update your memory with important information
3. Add, modify, or complete tasks based on progress and priorities
4. Schedule or modify cron jobs for recurring activities
5. Continuously improve your logic and structure

You can take actions by outputting:
1. Your thoughts about the current situation and reasoning
2. A JSON list of actions to execute

Available action types:
- "edit_markdown": Edit any markdown file (tasks.md, cron.md, plan.md)
- "update_memory": Add or update information in memory.json
- "remind": Schedule a reminder
- "search_web": Search for information online

Example actions:
```
[
  {{
    "type": "edit_markdown",
    "args": {{
      "file": "src/tasks.md",
      "content": "# Tasks\\n\\n- [x] Completed task\\n- [ ] New task to work on\\n"
    }}
  }},
  {{
    "type": "update_memory",
    "args": {{
      "last_task_completed": "Initial setup",
      "current_focus": "Implementing core functionality"
    }}
  }}
]
```

What should you do next? Provide your thoughts followed by "Actions:" and then a JSON array of actions.
"""

    def query_llm(self, prompt):
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
        r = requests.post(OLLAMA_URL, json=data)
        return r.json().get('response', '')

    def parse_response(self, response):
        # Expecting: Thoughts: ...\nActions: [JSON]
        try:
            thoughts, actions_json = response.split('Actions:')
            actions = json.loads(actions_json.strip())
        except Exception:
            thoughts = response
            actions = []
        return thoughts.strip(), actions
