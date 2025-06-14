import datetime
import json
import http.client  # Use built-in HTTP client instead of requests
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from utils import read_file, write_file

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'llama3.2'  # Using Llama3.2 for frontend interactions

class UserInteractionModel:
    """
    Handles all direct interactions with the user.
    Translates user needs into system tasks and presents results back to the user.
    """
    def __init__(self):
        self.conversation_history = []
        self.max_history_items = 10  # Keep last 10 exchanges for context
      
    def process_input(self, human_input, user_memory):
        """
        Process raw user input and translate it into system directives
        
        Args:
            human_input: Raw input from the user
            user_memory: User-facing portion of memory

        Returns:
            (thoughts, directives): Model thoughts and directives for the task execution system
        """
        # Add input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": human_input,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Trim history if it gets too long
        if len(self.conversation_history) > self.max_history_items:
            self.conversation_history = self.conversation_history[-self.max_history_items:]
        
        # Build prompt
        prompt = self.build_prompt(human_input, user_memory)
        
        # Query TinyLlama
        try:
            response = self.query_ollama(prompt, MODEL)
        except Exception as e:
            print(f"Error querying language model: {e}")
            return "Error processing input", []
        
        # Parse the response
        try:
            lines = response.split("\n")
            json_start = None
            json_end = None
            
            for i, line in enumerate(lines):
                if "```json" in line or "```JSON" in line:
                    json_start = i + 1
                elif json_start is not None and "```" in line:
                    json_end = i
                    break
            
            if json_start is not None and json_end is not None:
                json_str = "\n".join(lines[json_start:json_end])
                directives = json.loads(json_str)
                thoughts = "\n".join(lines[:json_start-1])
            else:
                # If no JSON found, attempt to extract it another way
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        directives = json.loads(json_match.group(0))
                        thoughts = response.replace(json_match.group(0), "").strip()
                    except:
                        directives = []
                        thoughts = response
                else:
                    directives = []
                    thoughts = response
        except Exception as e:
            print(f"Error parsing model response: {e}")
            thoughts = f"Failed to parse response: {response[:100]}..."
            directives = []
        
        # Add assistant response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": thoughts,
            "directives": directives,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return thoughts, directives
      
    def generate_output(self, execution_results, user_memory, full_response=None):
        """
        Generate a user-friendly response based on execution results
        
        Args:
            execution_results: Results from executing tasks
            user_memory: User-facing memory for context
            full_response: Full processed response object with any formatted data
            
        Returns:
            user_friendly_response: Response formatted for the user
        """        # Build prompt for response generation
        prompt = self.build_output_prompt(execution_results, user_memory, full_response)
        
        # Query model for response
        try:
            response = self.query_ollama(prompt, MODEL)
            return response
        except Exception as e:
            return f"I processed your request but encountered an error when generating a response: {e}"
    
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
            
    def build_prompt(self, human_input, user_memory):
        """
        Build a prompt for the model to process input
        
        Args:
            human_input: The raw input from the user
            user_memory: User-facing memory
            
        Returns:
            prompt: The complete prompt to send to the model
        """
        # Hidden system prompt - guides the model but isn't visible to user
        system_prompt = """You are the frontend component of a dual-model Life Assistant system, powered by Llama3.2.
        Your job is to understand what the user wants and convert it into structured directives that can be executed by the backend system.
        Focus on being helpful, accurate, and understanding the user's intent.
        Include only relevant sections based on the user's request.

        Available actions include:
        - update_memory: Store information in user memory
        - append_to_list: Add an item to a list in memory (e.g., friends, contracts)
        - remove_from_list: Remove an item from a list in memory
        - update_nested: Update a nested field in memory
        - retrieve_data: Request specific information from memory or tasks
        - Use when the user asks about previously stored information
        - Always use proper paths for common personal fields:
            - For name, use "personal.name" or "personal.full_name" 
            - For birthday preferences, use "personal.birthday_preferences"
            - For friends, use "personal.friends"
            - For health info, use "personal.health_conditions"
        - For sections without specific fields, use just the section name

        When responding to users, convert their natural language requests into appropriate backend actions.
        When users ask about personal information, always use retrieve_data with the proper path.
        """
        
        # Format the conversation history to provide context
        history = ""
        if self.conversation_history:
            for entry in self.conversation_history[-5:]:  # Include last 5 exchanges
                if entry['role'] == 'user':
                    history += f"User: {entry['content']}\n"
                else:
                    history += f"Assistant: {entry['content']}\n"
        
        # Format user memory for context
        memory_context = ""
        if user_memory:
            # Format tasks
            if 'tasks' in user_memory and user_memory['tasks']:
                memory_context += "Current Tasks:\n"
                for task_type, tasks in user_memory['tasks'].items():
                    if tasks:
                        memory_context += f"- {task_type.replace('_', ' ').title()}: {', '.join(str(t) for t in tasks)}\n"
            
            # Format personal preferences
            if 'personal' in user_memory and user_memory['personal']:
                memory_context += "\nPersonal Preferences:\n"
                for pref, value in user_memory['personal'].items():
                    memory_context += f"- {pref}: {value}\n"
        
        # Assemble the complete prompt
        complete_prompt = f"{system_prompt}\n\n"
        
        if history:
            complete_prompt += f"Conversation History:\n{history}\n\n"
            
        if memory_context:
            complete_prompt += f"User Context:\n{memory_context}\n\n"
            
        complete_prompt += f"Current Request: {human_input}\n\nYour response (thoughts followed by JSON directives):"
        
        return complete_prompt    
    
    def build_output_prompt(self, execution_results, user_memory, full_response=None):
        """
        Build a prompt for generating a user-friendly response
        Adds confirmations for memory/backend updates and ensures clear formatting.
        
        Args:
            execution_results: Results of task execution
            user_memory: User-facing memory
            full_response: Full response object with processed data
            
        Returns:
            prompt: The complete prompt for response generation
        """
        # Hidden system prompt
        system_prompt = """You are the frontend component of a dual-model Life Assistant system, powered by Llama3.2.
Your job is to take the execution results from the backend system and present them to the user in a friendly, helpful way.
Be concise, clear, and informative. Avoid technical jargon unless the user is technical.
Focus on what the user cares about most - did their request get fulfilled? What were the results?

When displaying information retrieved from memory:
- For simple values (numbers, plain text), show them in a natural way: "Your height is 1.94 meters"
- For birthday preferences or JSON-formatted strings:
  - If it looks like this: "{'occasion': 'birthdays', 'location': 'beach', 'with_family': true}"
  - Parse and present it nicely: "You prefer to celebrate birthdays at the beach with your family"
- For lists (like friends), present them in a readable format: "Your friends include John, Sarah, and Mike"
- If there's an error with data retrieval, apologize and explain simply what happened

If there were any issues or errors, explain them simply and suggest alternatives.
Be conversational and engaging, but stay focused on the user's original request.
Also, if any actions updated user memory, backend memory, or similar, provide a short confirmation (e.g., 'Your birthday preferences have been updated.').
"""

        # Format conversation history
        history = ""
        original_request = ""
        if self.conversation_history:
            # Get original request
            for entry in reversed(self.conversation_history):
                if entry['role'] == 'user':
                    original_request = entry['content']
                    break
                    
            # Include recent exchanges for context
            for entry in self.conversation_history[-4:]:  # Last 4 exchanges
                if entry['role'] == 'user':
                    history += f"User: {entry['content']}\n"
                else:
                    if 'directives' in entry:
                        # Just include the thoughts, not the directives
                        history += f"Assistant: {entry['content']}\n"
                    else:
                        history += f"Assistant: {entry['content']}\n"

        # Gather confirmations for memory/backend updates
        confirmations = []
        if full_response and isinstance(full_response, dict):
            for action in full_response.get('actions', []):
                t = action.get('type', '')
                args = action.get('args', {})
                if t in ("update_memory", "append_to_list", "remove_from_list", "update_nested"):
                    key = args.get('key', '')
                    if t == "update_memory":
                        confirmations.append(f"The information '{key}' has been updated.")
                    elif t == "append_to_list":
                        confirmations.append(f"Added '{args.get('value','')}' to {key}.")
                    elif t == "remove_from_list":
                        confirmations.append(f"Removed '{args.get('value','')}' from {key}.")
                    elif t == "update_nested":
                        confirmations.append(f"Updated '{key}' to '{args.get('value','')}'.")
                elif t == "update_backend_memory":
                    confirmations.append("Backend memory has been updated.")

        # Get retrieved data from response if available
        retrieved_data = ""
        if full_response and isinstance(full_response, dict):
            for action in full_response.get('actions', []):
                if action.get('type') == 'retrieve_data' and 'result' in action:
                    result = action.get('result', {})
                    if isinstance(result, dict):
                        
                        if 'formatted_data' in result:
                            retrieved_data += f"Retrieved data (formatted): {result['formatted_data']}\n"
                        elif 'data' in result:
                            retrieved_data += f"Retrieved data: {result['data']}\n"

        # Assemble the complete prompt
        complete_prompt = f"{system_prompt}\n\n"

        if history:
            complete_prompt += f"Conversation Context:\n{history}\n\n"

        complete_prompt += f"Original User Request: {original_request}\n\n"

        if confirmations:
            complete_prompt += f"System Confirmations:\n" + "\n".join(confirmations) + "\n\n"
        if retrieved_data:
            complete_prompt += f"Retrieved Information:\n{retrieved_data}\n\n"

        if execution_results:
            complete_prompt += f"Execution Results: {execution_results}\n\n"

        else:
            complete_prompt += "No specific execution results to report.\n\n"

        complete_prompt += "Your friendly response to the user:"
        
        return complete_prompt