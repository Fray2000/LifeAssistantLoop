#!/usr/bin/env python3

import sys
import os
import time
import json
import datetime
import http.client  # Built-in HTTP client instead of requests
import urllib.parse
import platform  # For platform detection
import threading
import re
import subprocess
import queue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from task_execution_model import TaskExecutionModel
from editor import Editor
from fixed_function_executor import FunctionExecutor
from memory_manager import MemoryManager
from utils import log_change, log_perception_action

# Path definitions
DATA_USER_DIR = os.path.join(BASE_DIR, 'data-user')
DATA_BACKEND_DIR = os.path.join(BASE_DIR, 'data-backend')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Communication files
HUMAN_INPUT_MD = os.path.join(SRC_DIR, 'human_input.md')
HUMAN_OUTPUT_MD = os.path.join(SRC_DIR, 'human_output.md')
REQUEST_FILE = os.path.join(SRC_DIR, 'backend_request.json')
RESPONSE_FILE = os.path.join(SRC_DIR, 'backend_response.json')
TASK_BUFFER_FILE = os.path.join(SRC_DIR, 'task_buffer.json')

# Memory files
USER_MEMORY = os.path.join(DATA_USER_DIR, 'memory.json')
BACKEND_MEMORY = os.path.join(DATA_BACKEND_DIR, 'backend_memory.json')

# Other files (move all backend-modified files to data-backend)
TASKS = os.path.join(DATA_BACKEND_DIR, 'tasks.md')
BACKEND_TASKS = os.path.join(DATA_BACKEND_DIR, 'backend_tasks.md')
CHANGE_LOG = os.path.join(DATA_BACKEND_DIR, 'change_log.md')
PERCEPTION_ACTION_LOG = os.path.join(DATA_BACKEND_DIR, 'perception_action.log')
BACKEND_LOG = os.path.join(DATA_BACKEND_DIR, 'backend_log.md')

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

class BackendLoop:
    """
    Backend component of the Life Assistant system.
    Continuously monitors for requests, processes tasks,
    and returns results to the frontend.
    """
    
    def __init__(self, debug_mode=False):
        """Initialize the backend components"""
        print(f"{Colors.HEADER}Initializing Life Assistant Backend...{Colors.ENDC}")
        
        self.task_model = TaskExecutionModel()    # Deepseek Coder for task execution
        self.editor = Editor()
        self.executor = FunctionExecutor()
        self.memory_manager = MemoryManager(USER_MEMORY, BACKEND_MEMORY, is_backend=True)
        self.debug_mode = debug_mode
        
        # Flag to indicate whether the system should exit
        self.should_exit = False
        
        # Timer for periodic tasks
        self.last_check_time = time.time()
        
        # Internal thoughts window
        self.internal_window = None
        self.thoughts_queue = queue.Queue()
        self.start_internal_window()
        
        # Update startup time in system memory
        self.memory_manager.update_system_memory({
            "system": {
                "backend_last_startup": datetime.datetime.now().isoformat(),
                "cycles_completed": self.memory_manager.get_system_memory().get("system", {}).get("cycles_completed", 0)
            }
        })
        
        self.ensure_directories_exist()
        print(f"{Colors.GREEN}Backend initialized and ready{Colors.ENDC}")
            
            
    def start_internal_window(self):
        """Start separate terminal windows for internal thoughts and task tree visualization"""
        try:
            # Create internal_thoughts.log if it doesn't exist
            thoughts_file = os.path.join(DATA_BACKEND_DIR, 'internal_thoughts.log')
            if not os.path.exists(thoughts_file):
                os.makedirs(os.path.dirname(thoughts_file), exist_ok=True)
                with open(thoughts_file, 'w', encoding='utf-8') as f:
                    f.write("")
            
            # Also make sure task_tree.log exists
            task_tree_file = os.path.join(DATA_BACKEND_DIR, 'task_tree.log')
            if not os.path.exists(task_tree_file):
                with open(task_tree_file, 'w', encoding='utf-8') as f:
                    f.write("{}")
            
            # Launch the dedicated windows in separate processes
            if platform.system() == "Windows":
                # Launch internal thoughts window
                self.internal_window = subprocess.Popen([
                    "powershell", "-Command", 
                    "Start-Process", "python", "-ArgumentList", 
                    f'"{os.path.join(BASE_DIR, "internal_window.py")}"'
                ])
                
                # Launch task tree window
                self.task_tree_window = subprocess.Popen([
                    "powershell", "-Command",
                    "Start-Process", "python", "-ArgumentList",
                    f'"{os.path.join(BASE_DIR, "task_tree_window.py")}"'
                ])
                
            elif platform.system() == "Darwin":  # macOS
                # Launch internal thoughts window
                self.internal_window = subprocess.Popen([
                    "osascript", "-e",
                    f'tell app "Terminal" to do script "python3 {os.path.join(BASE_DIR, "internal_window.py")}"'
                ])
                
                # Launch task tree window
                self.task_tree_window = subprocess.Popen([
                    "osascript", "-e", 
                    f'tell app "Terminal" to do script "python3 {os.path.join(BASE_DIR, "task_tree_window.py")}"'
                ])
                
            elif platform.system() == "Linux":
                # Try common terminal emulators
                terminals = ["gnome-terminal", "konsole", "xterm"]
                for terminal in terminals:
                    try:
                        # Launch internal thoughts window
                        self.internal_window = subprocess.Popen([
                            terminal, "--", "python3",
                            os.path.join(BASE_DIR, "internal_window.py")
                        ])
                        
                        # Launch task tree window
                        self.task_tree_window = subprocess.Popen([
                            terminal, "--", "python3",
                            os.path.join(BASE_DIR, "task_tree_window.py")
                        ])
                        break
                    except FileNotFoundError:
                        continue
            # Start thread to monitor thoughts queue
            self.thoughts_thread = threading.Thread(target=self._process_thoughts_queue, daemon=True)
            self.thoughts_thread.start()
            
            self.log_internal_thought("SUCCESS", "Internal thoughts window started")
            
        except Exception as e:
            print(f"{Colors.YELLOW}Could not start internal window: {e}{Colors.ENDC}")
            self.internal_window = None

    def _process_thoughts_queue(self):
        """Process thoughts from the queue and display in internal window"""
        while not self.should_exit:
            try:
                if not self.thoughts_queue.empty():
                    thought = self.thoughts_queue.get_nowait()
                    # In a real implementation, we would send this to the internal window
                    # For now, we'll just log it to a file that the window can read
                    self._write_thought_to_file(thought)
            except queue.Empty:
                pass
            except Exception as e:
                print(f"{Colors.RED}Error processing thoughts: {e}{Colors.ENDC}")
            time.sleep(0.1)

    def _write_thought_to_file(self, thought):
        """Write thought to a file that the internal window can monitor"""
        thoughts_file = os.path.join(DATA_BACKEND_DIR, 'internal_thoughts.log')
        try:
            with open(thoughts_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                f.write(f"[{timestamp}] {thought['type']}: {thought['content']}\n")
        except Exception as e:
            print(f"{Colors.RED}Error writing thought: {e}{Colors.ENDC}")

    def log_internal_thought(self, thought_type, content):
        """Log an internal thought to be displayed in the internal window"""
        if self.debug_mode or thought_type in ['ACTION', 'MEMORY', 'ERROR']:
            thought = {
                'type': thought_type,
                'content': content,
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.thoughts_queue.put(thought)
            
            # Also display in main console if debug mode
            if self.debug_mode:
                color_map = {
                    'THINKING': Colors.CYAN,
                    'ACTION': Colors.YELLOW,
                    'MEMORY': Colors.GREEN,
                    'TASK': Colors.PURPLE,
                    'ERROR': Colors.RED,
                    'SUCCESS': Colors.BLUE
                }
                color = color_map.get(thought_type, Colors.ENDC)
                print(f"{color}🧠 {thought_type}: {content}{Colors.ENDC}")

    def ensure_directories_exist(self):
        """Make sure all required directories exist"""
        os.makedirs(DATA_USER_DIR, exist_ok=True)
        os.makedirs(DATA_BACKEND_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(REQUEST_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(RESPONSE_FILE), exist_ok=True)
        
        # Touch files that might be needed
        if not os.path.exists(TASKS):
            directory = os.path.dirname(TASKS)
            os.makedirs(directory, exist_ok=True)
            with open(TASKS, 'w') as f:
                f.write("# Tasks\n\n")
        
        # Make sure communication files exist
        for file_path in [REQUEST_FILE, RESPONSE_FILE, TASK_BUFFER_FILE]:
            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    if file_path == TASK_BUFFER_FILE:
                        f.write(json.dumps([]))
                    else:
                        f.write(json.dumps({"status": "initialized"}))
        
        # Make sure log files exist
        for log_file in [CHANGE_LOG, PERCEPTION_ACTION_LOG, BACKEND_LOG]:
            directory = os.path.dirname(log_file)
            os.makedirs(directory, exist_ok=True)
            if not os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write(f"# {os.path.basename(log_file)} created on {datetime.datetime.now().isoformat()}\n\n")
        
        # Make sure backend tasks file exists
        if not os.path.exists(BACKEND_TASKS):
            directory = os.path.dirname(BACKEND_TASKS)
            os.makedirs(directory, exist_ok=True)
            with open(BACKEND_TASKS, 'w') as f:
                f.write("# Backend Tasks\n\n")

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

    def check_for_requests(self):
        """Check if there are any new requests from the frontend"""
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, 'r') as f:
                    request_data = json.load(f)
                    
                # Check if this is a new request we haven't processed
                last_processed = self.memory_manager.get_system_memory().get("internal_state", {}).get("last_processed_request_id")
                
                if "id" in request_data and request_data.get("id") != last_processed:
                    self.display_debug_info("New Request Detected", request_data)
                    return request_data
                    
            except json.JSONDecodeError:
                print(f"{Colors.RED}Error reading request file. Invalid JSON.{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}Error checking for requests: {e}{Colors.ENDC}")

        return None
    
    def process_request(self, request):
        """Process a request from the frontend, extract and store user info if found"""
        self.display_debug_info("Processing Request", request)
        self.log_internal_thought("ACTION", f"Processing new request: {request.get('id')}")
        
        cycle_num = self.memory_manager.get_system_memory().get("system", {}).get("cycles_completed", 0) + 1
        try:
            # Update last processed request id
            self.memory_manager.update_system_memory({
                "internal_state": {
                    "last_processed_request_id": request.get("id"),
                    "last_request_time": datetime.datetime.now().isoformat()
                }
            })
            
            # Check for active multi-cycle task sequences
            backend_mem = self.memory_manager.get_system_memory()
            multi_cycle = backend_mem.get('multi_cycle_tasks', {})
            current_sequence_id = multi_cycle.get('current_sequence_id')
            
            # If there's an active sequence, process it first
            if current_sequence_id and current_sequence_id in multi_cycle.get('active_sequences', {}):
                self.log_internal_thought("TASK", f"Continuing multi-cycle sequence: {current_sequence_id}")
                sequence_result = self._process_multi_cycle_sequence(current_sequence_id)
                if sequence_result:
                    # If sequence is complete or failed, process the new request normally
                    self.log_internal_thought("TASK", f"Multi-cycle sequence completed/failed, processing new request")
                else:
                    # Sequence is still active, return status update
                    response = {
                        "id": request.get("id"),
                        "status": "success",
                        "content": "Multi-cycle task sequence in progress. Next task will be processed automatically.",
                        "multi_cycle_status": "active",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    with open(RESPONSE_FILE, 'w') as f:
                        json.dump(response, f, indent=2)
                    return response
            
            directives = request.get("content", {})
            tasks = ""
            if os.path.exists(TASKS):
                with open(TASKS, 'r') as f:
                    tasks = f.read()
            
            self.log_internal_thought("THINKING", "Analyzing request with Deepseek Coder R1")
              # Check for multi-cycle tasks in progress
            system_memory = self.memory_manager.get_system_memory()
            multi_cycle = system_memory.get('multi_cycle_tasks', {})
            current_seq_id = multi_cycle.get('current_sequence_id')
            
            # If there's an active multi-cycle task sequence, get the current task
            current_task = None
            if current_seq_id:
                active_sequences = multi_cycle.get('active_sequences', {})
                if current_seq_id in active_sequences:
                    sequence = active_sequences[current_seq_id]
                    tasks_list = sequence.get('tasks', [])
                    current_idx = sequence.get('current_task_index', 0)
                    
                    if current_idx < len(tasks_list):
                        current_task = tasks_list[current_idx]
                        directives['current_multi_cycle_task'] = current_task
                        
                        self.log_internal_thought("TASK", f"Processing multi-cycle task: {current_task}")
                        self.log_internal_thought("TASK", f"Sequence: {sequence['name']} ({current_idx+1}/{len(tasks_list)})")
            
            # Execute directives with task execution model
            task_thoughts, actions, execution_results = self.task_model.execute_directives(
                directives,
                "",
                tasks,
                "",
                system_memory
            )
            
            self.log_internal_thought("THINKING", f"Generated {len(actions)} actions to execute")
            # --- New: Extract and store user info (e.g., height) ---
            user_info = {}
            # Example: extract height from thoughts or directives
            height_match = re.search(r'(?:height|tall|stature)[^\d]*(\d+(?:\.\d+)?\s*(?:cm|m|meters|feet|ft|inches|in))', str(directives) + ' ' + str(task_thoughts), re.IGNORECASE)
            if height_match:
                user_info['height'] = height_match.group(1).strip()
            # Store in user memory if found
            if user_info:
                user_mem = self.memory_manager.get_user_memory()
                if 'personal' not in user_mem:
                    user_mem['personal'] = {}
                user_mem['personal'].update(user_info)
                self.memory_manager.update_user_memory({'personal': user_mem['personal']})
            # --- End new ---            # Display debug info for Deepseek Coder R1's processing
            self.display_debug_info("Deepseek Coder R1 Thoughts", task_thoughts, Colors.YELLOW)
            self.display_debug_info("Deepseek Coder R1 Actions", actions, Colors.YELLOW)
            
            # Execute actions
            print(f"{Colors.YELLOW}Executing actions...{Colors.ENDC}")
            executed_actions = []
            
            for i, action in enumerate(actions):
                try:
                    action_type = action.get('type')
                    self.log_internal_thought("ACTION", f"Executing {action_type}: {action.get('args', {})}")
                    print(f"  {Colors.BLUE}▶ Action {i+1}/{len(actions)}: {action_type}{Colors.ENDC}")
                    
                    result = self.executor.execute(action, self.editor, self.memory_manager)
                    log_change(CHANGE_LOG, action, result)
                    
                    self.log_internal_thought("SUCCESS", f"Result: {result}")
                    
                    executed_actions.append({
                        "type": action_type,
                        "args": action.get("args", {}),
                        "result": result,
                        "success": True
                    })
                    
                    # Display debug info for action execution
                    self.display_debug_info(f"Action Result: {action.get('type')}", result, Colors.CYAN)
                    
                except Exception as e:
                    error_msg = f"Error in action {action.get('type')}: {e}"
                    print(f"{Colors.RED}❌ {error_msg}{Colors.ENDC}")
                    log_change(CHANGE_LOG, action, error_msg)
                    executed_actions.append({
                        "type": action.get("type"),
                        "args": action.get("args", {}),
                        "error": str(e),
                        "success": False
                    })
            
            # Create the response
            response = {
                "id": request.get("id"),
                "status": "success",
                "content": execution_results,
                "actions": executed_actions,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save the response
            with open(RESPONSE_FILE, 'w') as f:
                json.dump(response, f, indent=2)
                  # Update cycle count
            self.memory_manager.update_system_memory({
                "system": {
                    "cycles_completed": cycle_num
                }
            })
            
            # Handle multi-cycle task progression if applicable
            if current_seq_id:
                system_memory = self.memory_manager.get_system_memory()
                multi_cycle = system_memory.get('multi_cycle_tasks', {})
                active_sequences = multi_cycle.get('active_sequences', {})
                
                if current_seq_id in active_sequences:
                    sequence = active_sequences[current_seq_id]
                    current_idx = sequence.get('current_task_index', 0)
                    
                    # Mark current task as completed
                    sequence['completed_tasks'].append({
                        'task': sequence['tasks'][current_idx],
                        'completed_at': datetime.datetime.now().isoformat(),
                        'result': execution_results
                    })
                    
                    # Move to next task
                    current_idx += 1
                    sequence['current_task_index'] = current_idx
                    
                    # Check if sequence is complete
                    if current_idx >= len(sequence['tasks']):
                        sequence['status'] = 'completed'
                        self.log_internal_thought("TASK", f"Multi-cycle task sequence '{sequence['name']}' completed!")
                        
                        # Move to completed sequences
                        completed = multi_cycle.setdefault('completed_sequences', {})
                        completed[current_seq_id] = sequence
                        del active_sequences[current_seq_id]
                        
                        # Clear current sequence ID
                        multi_cycle['current_sequence_id'] = None
                    else:
                        self.log_internal_thought("TASK", f"Moving to next task in sequence: {sequence['tasks'][current_idx]}")
                        
                    # Save updated memory
                    self.memory_manager.update_system_memory(system_memory)
            
            self.display_debug_info("Response Created", response)
            self.log_internal_thought("SUCCESS", "Request processing complete")
            return response
                
        except Exception as e:
            error_msg = f"Error during request processing: {e}"
            print(f"{Colors.RED}❌ {error_msg}{Colors.ENDC}")
            
            # Create error response
            response = {
                "id": request.get("id"),
                "status": "error",
                "content": error_msg,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Save the error response
            with open(RESPONSE_FILE, 'w') as f:
                json.dump(response, f, indent=2)
                
            return response
    
    def check_for_system_tasks(self):
        """Check and execute periodic system tasks"""
        current_time = time.time()
        
        # If 5 minutes have passed since the last check
        if current_time - self.last_check_time > 300:
            self.last_check_time = current_time
            print(f"{Colors.CYAN}Performing periodic system checks...{Colors.ENDC}")
            
            # Check for tasks in the task buffer
            self.check_task_buffer()
            
            # Check for constant tasks that need to be executed
            self.check_constant_tasks()
            
            # Update last_check timestamp
            self.memory_manager.update_system_memory({
                "internal_state": {
                    "last_system_check": datetime.datetime.now().isoformat()
                }
            })

    def check_task_buffer(self):
        """Check for tasks in the buffer and process them"""
        if os.path.exists(TASK_BUFFER_FILE):
            try:
                with open(TASK_BUFFER_FILE, 'r') as f:
                    tasks = json.load(f)
                
                if tasks:
                    print(f"{Colors.YELLOW}Found {len(tasks)} tasks in buffer{Colors.ENDC}")
                    for task in tasks:
                        self.display_debug_info("Processing Task from Buffer", task)
                        
                        # Add task to backend processing queue
                        self.memory_manager.add_to_processing_queue(task)
                        
                        # Append execution to log
                        with open(BACKEND_LOG, 'a') as log_file:
                            log_file.write(f"[{datetime.datetime.now().isoformat()}] Received task: {task.get('description', 'No description')}\n")
                    
                    # Clear the buffer after processing
                    with open(TASK_BUFFER_FILE, 'w') as f:
                        json.dump([], f)
            except Exception as e:
                print(f"{Colors.RED}Error processing task buffer: {e}{Colors.ENDC}")
                  
                  
    def check_constant_tasks(self):
        """Check and process constant tasks that are due for execution"""
        due_tasks = self.memory_manager.get_due_constant_tasks()
        
        if due_tasks:
            print(f"{Colors.YELLOW}Found {len(due_tasks)} due constant tasks{Colors.ENDC}")
            
            for task in due_tasks:
                self.display_debug_info("Processing Constant Task", task)
                
                # Add task to processing queue
                self.memory_manager.add_to_processing_queue({
                    "description": task.get("description"),
                    "type": "constant",
                    "priority": task.get("priority", "medium")
                })
                
                # Update last execution time for the task
                task["last_executed"] = datetime.datetime.now().isoformat()
                
                # Append execution to log
                with open(BACKEND_LOG, 'a') as log_file:
                    log_file.write(f"[{datetime.datetime.now().isoformat()}] Executing constant task: {task.get('description')}\n")
                
            # Save memory to update task execution times
            self.memory_manager.save_memory()
    
    def _process_multi_cycle_sequence(self, sequence_id):
        """Process a specific task in a multi-cycle sequence
        
        Returns:
            bool: True if sequence is complete/failed, False if still active
        """
        system_memory = self.memory_manager.get_system_memory()
        multi_cycle = system_memory.get('multi_cycle_tasks', {})
        active_sequences = multi_cycle.get('active_sequences', {})
        
        if sequence_id not in active_sequences:
            self.log_internal_thought("ERROR", f"Cannot process sequence {sequence_id}: not found in active sequences")
            return True
            
        sequence = active_sequences[sequence_id]
        current_idx = sequence.get('current_task_index', 0)
        tasks = sequence.get('tasks', [])
        
        if current_idx >= len(tasks):
            # Sequence is already complete
            sequence['status'] = 'completed'
            self.log_internal_thought("TASK", f"Multi-cycle task sequence '{sequence['name']}' already completed!")
            
            # Move to completed sequences
            completed = multi_cycle.setdefault('completed_sequences', {})
            completed[sequence_id] = sequence
            del active_sequences[sequence_id]
            
            # Clear current sequence ID if this was the active one
            if multi_cycle.get('current_sequence_id') == sequence_id:
                multi_cycle['current_sequence_id'] = None
                
            # Save updated memory
            self.memory_manager.update_system_memory(system_memory)
            return True
            
        # Get the current task and update status
        current_task = tasks[current_idx]
        self.log_internal_thought("TASK", f"Processing multi-cycle task: {current_task}")
        self.log_internal_thought("TASK", f"Sequence: {sequence['name']} ({current_idx+1}/{len(tasks)})")
        
        # For now, we just update status - actual processing happens in process_request
        # The task execution is handled when the user makes their next request
        sequence['status'] = 'in_progress'
        self.memory_manager.update_system_memory(system_memory)
        
        return False
      
    def _process_multi_cycle_sequence(self, sequence_id):
        """Process a specific task in a multi-cycle sequence
        
        Returns:
            bool: True if sequence is complete/failed, False if still active
        """
        system_memory = self.memory_manager.get_system_memory()
        multi_cycle = system_memory.get('multi_cycle_tasks', {})
        active_sequences = multi_cycle.get('active_sequences', {})
        
        if sequence_id not in active_sequences:
            self.log_internal_thought("ERROR", f"Cannot process sequence {sequence_id}: not found in active sequences")
            return True
            
        sequence = active_sequences[sequence_id]
        current_idx = sequence.get('current_task_index', 0)
        tasks = sequence.get('tasks', [])
        
        if current_idx >= len(tasks):
            # Sequence is already complete
            sequence['status'] = 'completed'
            self.log_internal_thought("SEQUENCE", f"Multi-cycle task sequence '{sequence['name']}' already completed!")
            
            # Move to completed sequences
            completed = multi_cycle.setdefault('completed_sequences', {})
            completed[sequence_id] = sequence
            del active_sequences[sequence_id]
            
            # Clear current sequence ID if this was the active one
            if multi_cycle.get('current_sequence_id') == sequence_id:
                multi_cycle['current_sequence_id'] = None
                
            # Save updated memory
            self.memory_manager.update_system_memory(system_memory)
            return True
            
        # Get the current task and update status
        current_task = tasks[current_idx]
        self.log_internal_thought("MULTI_TASK", f"Processing multi-cycle task: {current_task}")
        self.log_internal_thought("SEQUENCE", f"Sequence: {sequence['name']} ({current_idx+1}/{len(tasks)})")
        
        # For now, we just update status - actual processing happens in process_request
        # The task execution is handled when the user makes their next request
        sequence['status'] = 'in_progress'
        self.memory_manager.update_system_memory(system_memory)
        
        return False
    
    def process_next_queue_task(self):
        """Process the next task in the processing queue"""
        task = self.memory_manager.get_next_task_from_queue()
        
        if task:
            self.display_debug_info("Processing Queue Task", task)
            
            # Execute the task
            # In a more sophisticated implementation, you would use the task_model to execute the task
            # For now, just log it and mark as completed
            result = f"Executed task: {task.get('description', 'No description')}"
            
            # Log execution
            with open(BACKEND_LOG, 'a') as log_file:
                log_file.write(f"[{datetime.datetime.now().isoformat()}] {result}\n")
                
            # Mark task as complete
            self.memory_manager.mark_task_complete(0, result)
            
            return True
        
        return False
    
    def run(self):
        """Run the backend loop continuously, prioritizing user requests over background tasks"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}Starting Life Assistant Backend Loop...{Colors.ENDC}")
        print(f"{Colors.CYAN}Press Ctrl+C at any time to exit.{Colors.ENDC}")
        
        try:
            while not self.should_exit:
                # 1. Check for user request
                request = self.check_for_requests()
                if request:
                    print(f"{Colors.GREEN}User request detected. Halting background tasks for this cycle.{Colors.ENDC}")
                    # Focus only on the user request for this cycle
                    self.process_request(request)
                    # After handling, continue to next loop iteration (skip background/queue processing)
                    continue
                any_work = False
                # 2. Move all tasks from buffer to processing queue
                if os.path.exists(TASK_BUFFER_FILE):
                    try:
                        with open(TASK_BUFFER_FILE, 'r') as f:
                            buffer_tasks = json.load(f)
                        if buffer_tasks:
                            for task in buffer_tasks:
                                self.memory_manager.add_to_processing_queue(task)
                                with open(BACKEND_LOG, 'a') as log_file:
                                    log_file.write(f"[{datetime.datetime.now().isoformat()}] Received task: {task.get('description', 'No description')}\n")
                            # Clear the buffer
                            with open(TASK_BUFFER_FILE, 'w') as f:
                                json.dump([], f)
                            self.memory_manager.save_memory()  # Persist after moving tasks
                            any_work = True
                    except Exception as e:
                        print(f"{Colors.RED}Error processing task buffer: {e}{Colors.ENDC}")
                # 3. Process all tasks in the processing queue
                while True:
                    task = self.memory_manager.get_next_task_from_queue()
                    if not task:
                        break
                    self.display_debug_info("Processing Queue Task", task)
                    result = f"Executed task: {task.get('description', 'No description')}"
                    with open(BACKEND_LOG, 'a') as log_file:
                        log_file.write(f"[{datetime.datetime.now().isoformat()}] {result}\n")
                    self.memory_manager.mark_task_complete(0, result)
                    any_work = True
                # 4. If no work was done, sleep briefly
                if not any_work:
                    time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}Stopping Life Assistant Backend...{Colors.ENDC}")
            self.should_exit = True
        finally:
            try:
                self.memory_manager.save_memory()
                print(f"{Colors.CYAN}Memory saved. Backend stopped.{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}Error saving memory on exit: {e}{Colors.ENDC}")

def start_backend(debug_mode=False):
    """Start the backend loop"""
    backend = BackendLoop(debug_mode=debug_mode)
    backend.run()

if __name__ == "__main__":
    debug_flag = "--debug" in sys.argv
    start_backend(debug_mode=debug_flag)
