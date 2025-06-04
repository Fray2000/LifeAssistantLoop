import json
import http.client  # Built-in HTTP client
import os

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'deepseek-coder:latest'  # Using Deepseek Coder R1 for backend execution
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
        
        # Query Deepseek Coder R1
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
        """        # System prompt for Deepseek Coder R1
        system_prompt = """You are Deepseek Coder R1, a powerful AI assistant responsible for planning and executing complex tasks.
        Your job is to take directives from the frontend system and convert them into concrete actions that can be executed.

        MEMORY STRUCTURE OVERVIEW:
        The user memory is now organized into comprehensive sections:
        - personal_info: profile, contact, appearance, preferences
        - health_and_wellness: medical_conditions, medications, doctors, fitness, diet, mental_health
        - calendar_and_events: events, reminders, availability_preferences
        - finance_and_banking: accounts, transactions, budgets, bills, investments, contracts
        - social_and_relationships: contacts, family_members, friend_groups, social_events
        - work_and_projects: current_job, projects, tasks, goals, documents
        - knowledge_and_learning: skills, education, courses, travel, vehicles, subscriptions
        - devices_and_smart_home: devices, routines
        - system_state: last_interaction, active_mode, current_focus
        - assistant_memory: conversation_history, learned_patterns, feedback

        MEMORY NAVIGATION GUIDELINES:
        - Use dot notation for nested paths: "personal_info.profile.full_name"
        - For health data: "health_and_wellness.medical_conditions"
        - For contacts: "social_and_relationships.contacts"
        - For work tasks: "work_and_projects.tasks.pending"
        - Always use the full path when updating or retrieving data        MULTI-CYCLE TASK MANAGEMENT:
        When a user request requires multiple steps or cycles to complete:
        1. Create a multi-cycle task sequence with individual steps
        2. Use "create_task_sequence" action to set up the sequence with these args:
           - sequence_name: Clear descriptive name for the sequence
           - tasks: Array of task descriptions, each representing one step
           - description: Detailed explanation of what this sequence accomplishes
        3. Each task in the sequence will be executed in order across multiple interactions
        4. The system will automatically track progress and move to the next task
        5. Use internal thoughts to explain what's happening during execution
        6. When detecting a complex multi-step request that needs consistent execution, 
           proactively create a task sequence rather than trying to do everything at once

        You must respond in this format:
        1. First, your thoughts and reasoning about the tasks (be thorough but concise)
        2. Then, a JSON array of actions to perform, enclosed in ```json``` tags

        Available actions:
        1. search_web: Search the web for information
        {"type": "search_web", "args": {"query": "search query"}}
        
        2. write_file: Write content to a file
        {"type": "write_file", "args": {"path": "/path/to/file", "content": "file content"}}
        
        3. add_task: Add a task to the task list
        {"type": "add_task", "args": {"task": "Task description", "priority": "high/medium/low"}}
        
        4. complete_task: Mark a task as completed
        {"type": "complete_task", "args": {"task": "Task description"}}
        
        5. update_memory: Store data in memory using full paths
        {"type": "update_memory", "args": {"key": "personal_info.profile.full_name", "value": "John Doe"}}
        
        6. append_to_list: Add an item to a list in memory
        {"type": "append_to_list", "args": {"key": "social_and_relationships.contacts", "value": {"name": "John", "relationship": "friend"}}}
        
        7. remove_from_list: Remove an item from a list in memory
        {"type": "remove_from_list", "args": {"key": "health_and_wellness.medications", "value": "aspirin"}}
        
        8. update_nested: Update a nested field in memory
        {"type": "update_nested", "args": {"key": "finance_and_banking.accounts.0.balance", "value": "1500.00"}}
        
        9. retrieve_data: Get specific information from memory or tasks
        - For specific fields: {"type": "retrieve_data", "args": {"data_type": "memory", "section": "personal_info.profile.age"}}
        - For entire sections: {"type": "retrieve_data", "args": {"data_type": "memory", "section": "health_and_wellness"}}
        - For search: {"type": "retrieve_data", "args": {"data_type": "memory", "query": "doctor"}}
        - For tasks: {"type": "retrieve_data", "args": {"data_type": "tasks", "query": "urgent"}}        10. create_task_sequence: Create a multi-cycle task sequence
        {"type": "create_task_sequence", "args": {"sequence_name": "Setup Health Profile", "tasks": ["Collect basic health information", "Record medical conditions", "Document medications"], "description": "Complete health profile setup for the user", "priority": "high"}}
        
        11. add_subtask: Add a subtask to an existing task
        {"type": "add_subtask", "args": {"parent_task_id": "task-123", "description": "Research medication side effects", "priority": "medium"}}

        MEMORY PATH EXAMPLES:
        - Personal info: "personal_info.profile.full_name", "personal_info.contact.email_addresses"
        - Health: "health_and_wellness.medical_conditions", "health_and_wellness.doctors_specialists"
        - Calendar: "calendar_and_events.events", "calendar_and_events.reminders"
        - Finance: "finance_and_banking.accounts", "finance_and_banking.budgets"
        - Social: "social_and_relationships.contacts", "social_and_relationships.family_members"
        - Work: "work_and_projects.current_job", "work_and_projects.tasks.pending"

        When handling retrieve_data:
        - Use exact field paths with dots for nested fields
        - Prefer direct field access over search queries when you know the exact location
        - If the user is asking for specific information they've stored before, use retrieve_data instead of guessing

        Be thoughtful about which actions to use based on the directives.
        Focus on understanding what the user wants and executing their request accurately.
        For complex requests, break them down into manageable steps and create task sequences.
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