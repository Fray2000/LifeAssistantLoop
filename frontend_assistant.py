#!/usr/bin/env python3

import time
import json
import os
import datetime
import http.client  # Built-in HTTP client instead of requests
import urllib.parse
import sys
import platform  # For platform detection
import threading
import uuid

# Only import readline on non-Windows platforms
if platform.system() != 'Windows':
    try:
        import readline  # For better command line editing on Unix
    except ImportError:
        pass  # Not critical, so continue if unavailable

from src.user_interaction_model import UserInteractionModel
from src.memory_manager import MemoryManager
from src.utils import log_change

# Path definitions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
DATA_USER_DIR = os.path.join(BASE_DIR, 'data-user')
DATA_BACKEND_DIR = os.path.join(BASE_DIR, 'data-backend')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Communication files
HUMAN_INPUT_MD = os.path.join(SRC_DIR, 'human_input.md')
HUMAN_OUTPUT_MD = os.path.join(SRC_DIR, 'human_output.md')
REQUEST_FILE = os.path.join(SRC_DIR, 'backend_request.json')
RESPONSE_FILE = os.path.join(SRC_DIR, 'backend_response.json')
TASK_BUFFER_FILE = os.path.join(SRC_DIR, 'task_buffer.json')

# Other files
USER_MEMORY = os.path.join(DATA_USER_DIR, 'memory.json')
INTERACTION_LOG = os.path.join(LOGS_DIR, 'interaction.log')

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    PURPLE = '\033[95m'
    GRAY = '\033[90m'

# Function to make HTTP requests using built-in http.client
def make_ollama_request(prompt, model="llama3.2"):
    """Make a request to Ollama API using built-in http.client"""
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
        return f"Error connecting to Ollama: {e}"

class FrontendAssistant:
    """
    Frontend component of the Life Assistant system.
    Handles direct user interactions and communicates with backend for task execution.
    """
    
    def __init__(self):
        """Initialize the assistant components"""
        print(f"{Colors.HEADER}Initializing Life Assistant Frontend...{Colors.ENDC}")
        
        # Check if Ollama is available
        try:
            test_response = make_ollama_request("Test", model="llama3.2")
            print(f"{Colors.GREEN}Successfully connected to Ollama{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Warning: Could not connect to Ollama. Make sure it's running: {e}{Colors.ENDC}")
        
        self.user_model = UserInteractionModel()  # Llama3.2 for user interaction
        self.memory_manager = MemoryManager(USER_MEMORY)  # Only initialize with user memory
        
        # Flag to indicate whether the system is processing a request
        self.processing = False
        # Flag to indicate if the system should exit
        self.should_exit = False
        
        # Debug mode flag
        self.debug_mode = False
        
        # Request tracking
        self.current_request_id = None
        self.last_response_id = None
        self.waiting_for_response = False
        
        # Update startup time in system memory
        self.memory_manager.update_system_memory({
            "system": {
                "frontend_last_startup": datetime.datetime.now().isoformat()
            }
        })
        
        self.ensure_directories_exist()
        print(f"{Colors.GREEN}Frontend initialized and ready{Colors.ENDC}")
        
    def ensure_directories_exist(self):
        """Make sure all required directories exist"""
        os.makedirs(DATA_USER_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(HUMAN_INPUT_MD), exist_ok=True)
        os.makedirs(os.path.dirname(HUMAN_OUTPUT_MD), exist_ok=True)
        os.makedirs(os.path.dirname(REQUEST_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(RESPONSE_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(TASK_BUFFER_FILE), exist_ok=True)
        
        # Make sure log files exist
        if not os.path.exists(INTERACTION_LOG):
            directory = os.path.dirname(INTERACTION_LOG)
            os.makedirs(directory, exist_ok=True)
            with open(INTERACTION_LOG, 'w') as f:
                f.write(f"# {os.path.basename(INTERACTION_LOG)} created on {datetime.datetime.now().isoformat()}\n\n")
        
        # Make sure task buffer file exists
        if not os.path.exists(TASK_BUFFER_FILE):
            directory = os.path.dirname(TASK_BUFFER_FILE)
            os.makedirs(directory, exist_ok=True)
            with open(TASK_BUFFER_FILE, 'w') as f:
                f.write(json.dumps([]))

    def get_user_input(self):
        """Get input from the user via terminal"""
        try:
            print(f"\n{Colors.BOLD}{Colors.BLUE}You:{Colors.ENDC} ", end="")
            user_input = input()
            
            # Check for debug command
            if user_input.lower() == "debug on":
                self.debug_mode = True
                print(f"{Colors.PURPLE}Debug mode enabled. You'll see internal model interactions.{Colors.ENDC}")
                return self.get_user_input()  # Get another input
            elif user_input.lower() == "debug off":
                self.debug_mode = False
                print(f"{Colors.PURPLE}Debug mode disabled.{Colors.ENDC}")
                return self.get_user_input()  # Get another input
            
            return user_input
        except KeyboardInterrupt:
            print("\nExiting...")
            self.should_exit = True
            return "exit"
            
    def display_assistant_response(self, response):
        """Display the assistant's response in the terminal"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}Assistant:{Colors.ENDC}")
        
        # Display the response with nice line wrapping
        lines = response.split('\n')
        try:
            terminal_width = os.get_terminal_size().columns
        except:
            terminal_width = 80  # Default width if terminal size can't be determined
            
        for line in lines:
            if len(line) > terminal_width - 10:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 > terminal_width - 10:
                        print(f"  {current_line}")
                        current_line = word
                    else:
                        if current_line:
                            current_line += " " + word
                        else:
                            current_line = word
                if current_line:
                    print(f"  {current_line}")
            else:
                print(f"  {line}")
        print()  # Add an empty line for better separation
            
    def display_debug_info(self, title, content, color=Colors.GRAY):
        """Display debug information in the terminal"""
        if not self.debug_mode:
            return
            
        print(f"\n{color}===== DEBUG: {title} ====={Colors.ENDC}")
        
        # If content is a dict or list, pretty print it
        if isinstance(content, (dict, list)):
            try:
                content_str = json.dumps(content, indent=2)
                print(f"{color}{content_str}{Colors.ENDC}")
            except:
                print(f"{color}{content}{Colors.ENDC}")
        else:
            # Limit the output to prevent flooding the terminal
            if isinstance(content, str) and len(content) > 500:
                print(f"{color}{content[:500]}... (truncated){Colors.ENDC}")
            else:
                print(f"{color}{content}{Colors.ENDC}")
                
        print(f"{color}{'='*40}{Colors.ENDC}")
    
    def send_request_to_backend(self, user_input, request_type="command"):
        """Send a request to the backend"""
        self.display_debug_info("Sending Request to Backend", user_input, Colors.PURPLE)
        request_id = str(uuid.uuid4())
        self.current_request_id = request_id
        
        # Create the request
        request = {
            "id": request_id,
            "type": request_type,
            "content": user_input,
            "timestamp": datetime.datetime.now().isoformat(),
            "response_required": True
        }
        
        # Save the request to the file
        with open(REQUEST_FILE, 'w') as f:
            json.dump(request, f, indent=2)
            
        return request_id
    
    def add_task_to_buffer(self, task):
        """Add a task to the buffer for backend processing"""
        try:
            current_tasks = []
            if os.path.exists(TASK_BUFFER_FILE):
                with open(TASK_BUFFER_FILE, 'r') as f:
                    current_tasks = json.load(f)
            
            # Add the new task
            current_tasks.append(task)
            
            # Write back to buffer
            with open(TASK_BUFFER_FILE, 'w') as f:
                json.dump(current_tasks, f, indent=2)
                
            self.display_debug_info("Added Task to Buffer", task)
            return True
        except Exception as e:
            print(f"{Colors.RED}Error adding task to buffer: {e}{Colors.ENDC}")
            return False
    
    def check_backend_response(self, request_id):
        """Check if the backend has responded to our request"""
        if os.path.exists(RESPONSE_FILE):
            try:
                with open(RESPONSE_FILE, 'r') as f:
                    response = json.load(f)
                    
                # Check if this is the response to our request
                if response.get("id") == request_id and response.get("id") != self.last_response_id:
                    self.last_response_id = response.get("id")
                    self.display_debug_info("Received Backend Response", response, Colors.PURPLE)
                    return response
            except json.JSONDecodeError:
                print(f"{Colors.RED}Error reading response file. Invalid JSON.{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}Error checking backend response: {e}{Colors.ENDC}")
                
        return None
    
    def process_request(self, user_input):
        """Process a user request by coordinating with backend"""
        self.processing = True
        
        try:
            # Update last interaction time
            self.memory_manager.update_user_memory({
                "last_interaction": datetime.datetime.now().isoformat()
            })
            
            # Process with user model (frontend)
            print(f"{Colors.YELLOW}Processing your request...{Colors.ENDC}")
            user_thoughts, directives = self.user_model.process_input(
                user_input, 
                self.memory_manager.get_user_memory()
            )

            # --- NEW: Handle memory update actions for lists (e.g., friends) ---
            if isinstance(directives, dict) and "actions" in directives:
                for action in directives["actions"]:
                    if action.get("type") == "update_memory":
                        args = action.get("args", {})
                        memory_type = args.get("memory_type")
                        key = args.get("key")
                        value = args.get("value")
                        if memory_type == "user" and key:
                            # Support appending to lists (e.g., friends)
                            if key.startswith("personal.friends") and isinstance(value, str):
                                user_mem = self.memory_manager.get_user_memory()
                                friends = user_mem.get("personal", {}).get("friends", [])
                                if value not in friends:
                                    update = {"personal": {"friends": friends + [value]}}
                                    self.memory_manager.update_user_memory(update)
                            # Support nested keys like "personal.full_name"
                            elif "." in key:
                                parts = key.split(".")
                                update = curr = {}
                                for p in parts[:-1]:
                                    curr[p] = {}
                                    curr = curr[p]
                                curr[parts[-1]] = value
                                self.memory_manager.update_user_memory(update)
                            else:
                                self.memory_manager.update_user_memory({key: value})
            # --- END NEW ---

            # Check if any background tasks should be scheduled
            if "background_tasks" in user_thoughts:
                for task in user_thoughts["background_tasks"]:
                    self.add_task_to_buffer({
                        "description": task,
                        "priority": "medium",
                        "type": "background",
                        "added_at": datetime.datetime.now().isoformat(),
                        "status": "pending"
                    })
            
            # Display debug info for processing
            self.display_debug_info("Frontend Model Thoughts", user_thoughts, Colors.PURPLE)
            self.display_debug_info("Frontend Model Directives", directives, Colors.PURPLE)
            
            # Log user interaction
            with open(INTERACTION_LOG, 'a') as f:
                f.write(f"\n[{datetime.datetime.now().isoformat()}] USER: {user_input}\n")
                f.write(f"DIRECTIVES: {json.dumps(directives, indent=2)}\n")
            
            # Send request to backend
            print(f"{Colors.YELLOW}Sending request to backend...{Colors.ENDC}")
            request_id = self.send_request_to_backend(directives)
            self.waiting_for_response = True
            
            # Wait for backend response
            print(f"{Colors.YELLOW}Waiting for backend to process request...{Colors.ENDC}")
            max_wait_time = 60  # Maximum wait time in seconds
            start_time = time.time()
            
            while self.waiting_for_response and (time.time() - start_time) < max_wait_time:
                response = self.check_backend_response(request_id)
                
                if response:
                    self.waiting_for_response = False
                    
                    if response.get("status") == "error":
                        print(f"{Colors.RED}Backend error: {response.get('content')}{Colors.ENDC}")
                        error_msg = f"I'm sorry, there was a problem processing your request: {response.get('content')}"
                        self.display_assistant_response(error_msg)
                        break
                        
                    # Get execution results from the backend
                    execution_results = response.get("content", "")
                    
                    # Generate user-friendly output based on backend results
                    print(f"{Colors.YELLOW}Generating response...{Colors.ENDC}")
                    human_friendly_output = self.user_model.generate_output(
                        execution_results,
                        self.memory_manager.get_user_memory()
                    )
                    
                    # Display debug info for final output generation
                    self.display_debug_info("Final Response Generation", 
                                           f"Based on execution results: {execution_results}", 
                                           Colors.PURPLE)
                    
                    # Log the output
                    with open(INTERACTION_LOG, 'a') as f:
                        f.write(f"ASSISTANT: {human_friendly_output}\n")
                        f.write("-"*50 + "\n")
                    
                    # Display response to user
                    self.display_assistant_response(human_friendly_output)
                    break
                
                time.sleep(0.5)  # Check every half second
                
            if self.waiting_for_response:
                # Timeout occurred
                print(f"{Colors.RED}Timeout waiting for backend response.{Colors.ENDC}")
                timeout_msg = "I'm sorry, the backend is taking too long to respond. Please try again later."
                self.display_assistant_response(timeout_msg)
                self.waiting_for_response = False
                
        except Exception as e:
            error_msg = f"Error during processing: {e}"
            print(f"{Colors.RED}❌ {error_msg}{Colors.ENDC}")
            human_friendly_output = "I encountered an issue while processing your request. Please try again or rephrase."
            self.display_assistant_response(human_friendly_output)
        
        self.processing = False
        return

    def run(self):
        """Run the assistant in interactive terminal mode"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}Starting Life Assistant in Interactive Terminal Mode...{Colors.ENDC}")
        print(f"{Colors.CYAN}Type 'exit' to quit. Press Ctrl+C at any time to exit.{Colors.ENDC}")
        print(f"{Colors.CYAN}Type 'debug on' to see internal model interactions, 'debug off' to hide them.{Colors.ENDC}")
        
        # Print welcome message
        welcome_msg = "I'm your Life Assistant powered by Llama3.2. How can I help you today?"
        self.display_assistant_response(welcome_msg)
        
        while not self.should_exit:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                # Check for exit command
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print(f"\n{Colors.CYAN}Exiting Life Assistant. Goodbye!{Colors.ENDC}")
                    break
                
                # Process the request in the main thread
                if user_input.strip():
                    self.process_request(user_input)
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.CYAN}Stopping Life Assistant...{Colors.ENDC}")
                break
            except Exception as e:
                print(f"{Colors.RED}Unexpected error: {e}{Colors.ENDC}")
                time.sleep(1)  # Brief pause before retrying

if __name__ == '__main__':
    try:
        assistant = FrontendAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt.")
    finally:
        # Make sure memory is saved on exit
        try:
            if 'assistant' in locals():
                assistant.memory_manager.save_memory()
                print(f"{Colors.CYAN}Memory saved. Frontend stopped.{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}Error saving memory on exit: {e}{Colors.ENDC}")
