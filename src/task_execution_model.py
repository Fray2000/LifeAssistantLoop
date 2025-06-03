import json
import http.client  # Built-in HTTP client
import os

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'llama3.2'  # Using Llama3.2 for backend execution
DEFAULT_TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data-backend', 'tasks.md')

class TaskExecutionModel:
    """
    Handles complex reasoning and task execution planning.
    Generates concrete actions based on directives from the user interaction model.
    """
    
    def execute_directives(self, directives, plan, tasks=None, cron=None, system_memory=None):
        """
        Process directives from the user interaction model and determine actions
        
        Args:
            directives: Structured directives from the user model
            plan: Current plan (not used in simplified version)
            tasks: Current tasks
            cron: Current cron tasks (not used in simplified version)
            system_memory: System memory for context
            
        Returns:
            (thoughts, actions, results): Model thoughts, planned actions, and execution results
        """
        if tasks is None:
            with open(DEFAULT_TASKS_FILE, 'r') as f:
                tasks = f.read()
        
        # Build the execution prompt
        prompt = self.build_execution_prompt(directives, plan, tasks, cron, system_memory)
        
        # Query Llama3.2
        try:
            response = self.query_ollama(prompt, MODEL)
        except Exception as e:
            print(f"Error querying execution model: {e}")
            return f"Error querying execution model: {e}", [], "Error occurred during processing"
        
        # Parse the response to extract thoughts and actions
        try:
            # Split into thoughts and JSON actions
            thoughts = ""
            actions = []
            action_json = ""
            
            lines = response.split('\n')
            json_start = None
            json_end = None
            
            for i, line in enumerate(lines):
                if "```json" in line or "```JSON" in line:
                    json_start = i + 1
                elif json_start is not None and "```" in line:
                    json_end = i
                    break
            
            if json_start is not None and json_end is not None:
                thoughts = "\n".join(lines[:json_start-1])
                action_json = "\n".join(lines[json_start:json_end])
                try:
                    actions = json.loads(action_json)
                except json.JSONDecodeError as e:
                    thoughts += f"\nError parsing actions JSON: {e}"
                    actions = []
            else:
                # If no JSON found, attempt to extract it another way
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    try:
                        actions = json.loads(json_match.group(0))
                        thoughts = response.replace(json_match.group(0), "").strip()
                    except Exception as e:
                        thoughts = response
                        actions = []
                else:
                    thoughts = response
                    actions = []
                
        except Exception as e:
            thoughts = f"Error parsing model response: {e}\n{response[:200]}..."
            actions = []
        
        # Execution results summary
        if actions:
            results = f"Generated {len(actions)} actions to fulfill your request."
        else:
            results = "I understood your request but couldn't determine specific actions to take."
            
        return thoughts, actions, results

    def query_ollama(self, prompt, model=MODEL):
        """
        Query Ollama API using built-in http client
        
        Args:
            prompt: The prompt to send to the model
            model: The model name to use
            
        Returns:
            response_text: The model's response
        """
        try:
            conn = http.client.HTTPConnection("localhost", 11434)
            headers = {'Content-Type': 'application/json'}
            
            payload = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False
            })
            
            conn.request("POST", "/api/generate", payload, headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            conn.close()
            
            response_json = json.loads(data)
            return response_json.get('response', 'No response from model')
        except Exception as e:
            raise Exception(f"Failed to query Ollama: {e}")

    def build_execution_prompt(self, directives, plan, tasks, cron, system_memory):
        """
        Build a prompt for the execution model
        
        Args:
            directives: Structured directives from user model
            plan: Current plan (not used in simple version)
            tasks: Current tasks
            cron: Current cron tasks (not used in simple version)
            system_memory: System memory
            
        Returns:
            prompt: Complete prompt for execution model
        """
        # System prompt for llama3.2
        system_prompt = """You are Llama3.2, a powerful assistant responsible for planning and executing tasks.
Your job is to take directives from the frontend system and convert them into concrete actions that can be executed.

You must respond in this format:
1. First, your thoughts and reasoning about the tasks (be thorough but concise)
2. Then, a JSON array of actions to perform, enclosed in ```json``` tags

Available actions:
1. search_web: Search the web for information
   {"type": "search_web", "args": {"query": "search query"}}

2. add_task: Add a new task to the task list
   {"type": "add_task", "args": {"task": "Task description", "priority": "high|medium|low"}}

3. complete_task: Mark a task as completed
   {"type": "complete_task", "args": {"task_index": 0}}

4. update_task: Update a task's description or priority
   {"type": "update_task", "args": {"task_index": 0, "new_description": "New description", "new_priority": "high|medium|low"}}

5. write_file: Write content to a file
   {"type": "write_file", "args": {"path": "path/to/file.txt", "content": "File content"}}

6. update_memory: Update user or system memory
   {"type": "update_memory", "args": {"memory_type": "user|system", "key": "path.to.key", "value": "New value"}}

7. calculate: Perform a calculation
   {"type": "calculate", "args": {"expression": "1 + 1"}}

8. get_date: Get the current date/time
   {"type": "get_date", "args": {}}

Make sure your actions are properly formatted as a JSON array.
"""
        
        # Format the directives
        directives_str = json.dumps(directives, indent=2) if directives else "No directives provided"
        
        # Format the tasks
        tasks_str = tasks if tasks else "No tasks available"
        
        # Build the complete prompt
        complete_prompt = f"{system_prompt}\n\n"
        complete_prompt += f"DIRECTIVES:\n{directives_str}\n\n"
        complete_prompt += f"CURRENT TASKS:\n{tasks_str}\n\n"
        
        complete_prompt += "Your response (thoughts followed by JSON actions array):"
        
        return complete_prompt