import requests
import json
from .utils import read_file, write_file

OLLAMA_URL = 'http://umbrel.local:11434/api/generate'
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
You are an autonomous life assistant agent. Follow the deployment plan strictly.

Deployment Plan:\n{deployment_plan}\n
Project Plan:\n{plan}\n
Tasks:\n{tasks}\n
Cron:\n{cron}\n
Human Input:\n{human_input}\n
Memory:\n{json.dumps(memory)}\n
What should you do next? List your thoughts and a list of structured actions (as JSON)."""

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
