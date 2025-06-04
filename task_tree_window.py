#!/usr/bin/env python3
"""
Task Tree Window for the Life Assistant Backend
Displays a hierarchical tree view of backend tasks, subtasks, and their priorities
"""

import os
import sys
import time
import json
import datetime
import threading
import queue
import random

# Path definitions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_BACKEND_DIR = os.path.join(BASE_DIR, 'data-backend')
BACKEND_MEMORY_PATH = os.path.join(DATA_BACKEND_DIR, 'backend_memory.json')
TASK_TREE_LOG = os.path.join(DATA_BACKEND_DIR, 'task_tree.log')

# Define colors for different priority levels and task states
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
    ORANGE = '\033[38;5;208m'
    
    # Priority colors
    HIGH = '\033[91m'    # Red for high priority
    MEDIUM = '\033[93m'  # Yellow for medium priority
    LOW = '\033[94m'     # Blue for low priority
    
    # Task state colors
    PENDING = '\033[90m'    # Gray for pending tasks
    IN_PROGRESS = '\033[93m'  # Yellow for in-progress tasks
    COMPLETED = '\033[92m'    # Green for completed tasks
    FAILED = '\033[91m'       # Red for failed tasks

class TaskTreeWindow:
    """Display the backend task tree in a separate window"""
    
    def __init__(self):
        """Initialize the task tree window"""
        self.running = True
        self.last_check_time = time.time()
        self.thread_stop_event = threading.Event()
        
        # Task tree structure
        self.task_tree = {}
        
        # Icons for tree visualization
        self.icons = {
            'branch': '├── ',
            'last_branch': '└── ',
            'continuation': '│   ',
            'empty': '    ',
            'high_priority': '🔴 ',
            'medium_priority': '🟡 ',
            'low_priority': '🔵 ',
            'pending': '⭕ ',
            'in_progress': '▶️ ',
            'completed': '✅ ',
            'failed': '❌ '
        }
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the window header"""
        self.clear_screen()
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}📊 TASK TREE VISUALIZATION 📊{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.PURPLE}This window displays a hierarchical tree of backend tasks, subtasks, and their priorities.{Colors.ENDC}")
        print(f"{Colors.PURPLE}Tasks are color-coded by priority and status.{Colors.ENDC}")
        print()
        
        # Print legend
        print(f"{Colors.BOLD}Legend:{Colors.ENDC}")
        print(f"{Colors.HIGH}{self.icons['high_priority']}High Priority{Colors.ENDC}  ", end="")
        print(f"{Colors.MEDIUM}{self.icons['medium_priority']}Medium Priority{Colors.ENDC}  ", end="")
        print(f"{Colors.LOW}{self.icons['low_priority']}Low Priority{Colors.ENDC}")
        
        print(f"{Colors.PENDING}{self.icons['pending']}Pending{Colors.ENDC}  ", end="")
        print(f"{Colors.IN_PROGRESS}{self.icons['in_progress']}In Progress{Colors.ENDC}  ", end="")
        print(f"{Colors.COMPLETED}{self.icons['completed']}Completed{Colors.ENDC}  ", end="")
        print(f"{Colors.FAILED}{self.icons['failed']}Failed{Colors.ENDC}")
        
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print()
    
    def load_task_data(self):
        """Load task data from backend memory file"""
        try:
            if os.path.exists(BACKEND_MEMORY_PATH):
                with open(BACKEND_MEMORY_PATH, 'r') as f:
                    backend_memory = json.load(f)
                
                # Get current time for age calculation
                now = datetime.datetime.now()
                
                # Extract tasks from various sources in backend memory
                task_tree = {
                    "processing_queue": [],
                    "constant_tasks": [],
                    "multi_cycle_tasks": [],
                    "next_cycle_plan": []
                }
                
                # Process the queue tasks
                if "processing_queue" in backend_memory:
                    for task in backend_memory["processing_queue"]:
                        task_info = self._extract_task_info(task, now)
                        if task_info:
                            task_tree["processing_queue"].append(task_info)
                
                # Process constant tasks
                if "constant_tasks" in backend_memory:
                    for task in backend_memory["constant_tasks"]:
                        task_info = self._extract_task_info(task, now)
                        if task_info:
                            task_tree["constant_tasks"].append(task_info)
                
                # Process multi-cycle tasks
                if "multi_cycle_tasks" in backend_memory:
                    multi_cycle = backend_memory.get("multi_cycle_tasks", {})
                    active_sequences = multi_cycle.get("active_sequences", {})
                    completed_sequences = multi_cycle.get("completed_sequences", {})
                    current_id = multi_cycle.get("current_sequence_id")
                    
                    # Process active sequences
                    for seq_id, sequence in active_sequences.items():
                        seq_info = {
                            "id": seq_id,
                            "name": sequence.get("name", "Unnamed Sequence"),
                            "description": sequence.get("description", ""),
                            "status": sequence.get("status", "pending"),
                            "priority": sequence.get("priority", "medium"),
                            "is_current": seq_id == current_id,
                            "progress": {
                                "current": sequence.get("current_task_index", 0),
                                "total": len(sequence.get("tasks", []))
                            },
                            "tasks": []
                        }
                        
                        # Add individual tasks in the sequence
                        tasks = sequence.get("tasks", [])
                        current_idx = sequence.get("current_task_index", 0)
                        completed_tasks = [t.get("task") for t in sequence.get("completed_tasks", [])]
                        
                        for i, task in enumerate(tasks):
                            status = "completed" if i < current_idx else \
                                    "in_progress" if i == current_idx else "pending"
                            
                            task_info = {
                                "description": task,
                                "status": status,
                                "index": i,
                                "priority": sequence.get("priority", "medium")
                            }
                            seq_info["tasks"].append(task_info)
                        
                        task_tree["multi_cycle_tasks"].append(seq_info)
                
                # Process next cycle plan
                if "next_cycle_plan" in backend_memory:
                    for task in backend_memory.get("next_cycle_plan", []):
                        task_info = self._extract_task_info(task, now)
                        if task_info:
                            task_tree["next_cycle_plan"].append(task_info)
                
                self.task_tree = task_tree
                return task_tree
            else:
                return {"error": "Backend memory file not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_task_info(self, task_data, now):
        """Extract relevant task information from task data"""
        if isinstance(task_data, dict):
            # Handle different task formats
            description = ""
            status = "pending"
            priority = "medium"
            created_at = None
            
            # Extract task description
            if "description" in task_data:
                description = task_data["description"]
            elif "task" in task_data and isinstance(task_data["task"], dict):
                description = task_data["task"].get("description", "No description")
            elif "task" in task_data and isinstance(task_data["task"], str):
                description = task_data["task"]
                
            # Extract status
            if "status" in task_data:
                status = task_data["status"]
            
            # Extract priority
            if "priority" in task_data:
                priority = task_data["priority"]
            elif "task" in task_data and isinstance(task_data["task"], dict):
                priority = task_data["task"].get("priority", "medium")
            
            # Extract timestamp
            if "added_at" in task_data:
                created_at = task_data["added_at"]
            elif "created_at" in task_data:
                created_at = task_data["created_at"]
            
            # Calculate age if timestamp available
            age = None
            if created_at:
                try:
                    created_time = datetime.datetime.fromisoformat(created_at)
                    delta = now - created_time
                    if delta.days > 0:
                        age = f"{delta.days}d {delta.seconds // 3600}h"
                    else:
                        minutes = delta.seconds // 60
                        if minutes >= 60:
                            age = f"{minutes // 60}h {minutes % 60}m"
                        else:
                            age = f"{minutes}m"
                except:
                    pass
            
            return {
                "description": description,
                "status": status,
                "priority": priority,
                "age": age,
                "subtasks": task_data.get("subtasks", [])
            }
        return None
    
    def display_task_tree(self):
        """Display the task tree with proper formatting"""
        task_tree = self.load_task_data()
        
        if "error" in task_tree:
            print(f"{Colors.RED}Error loading task data: {task_tree['error']}{Colors.ENDC}")
            return
        
        # Display multi-cycle tasks first (most important)
        if task_tree["multi_cycle_tasks"]:
            print(f"{Colors.BOLD}🔄 MULTI-CYCLE TASK SEQUENCES{Colors.ENDC}")
            for sequence in task_tree["multi_cycle_tasks"]:
                # Determine sequence status color
                status_color = Colors.PENDING
                if sequence["status"] == "in_progress":
                    status_color = Colors.IN_PROGRESS
                elif sequence["status"] == "completed":
                    status_color = Colors.COMPLETED
                elif sequence["status"] == "failed":
                    status_color = Colors.FAILED
                
                # Get priority color and icon
                priority_color = self._get_priority_color(sequence["priority"])
                priority_icon = self._get_priority_icon(sequence["priority"])
                
                # Format current marker
                current_marker = " ⭐ CURRENT" if sequence["is_current"] else ""
                
                # Format sequence header
                progress = f"{sequence['progress']['current']}/{sequence['progress']['total']}"
                percentage = int((sequence['progress']['current'] / max(1, sequence['progress']['total'])) * 100)
                progress_bar = self._create_progress_bar(percentage)
                
                print(f"{priority_color}{self.icons['branch']}{priority_icon}{sequence['name']}{Colors.ENDC} "
                      f"{status_color}[{sequence['status'].upper()}]{Colors.ENDC}{current_marker}")
                
                # Show sequence description if present
                if sequence["description"]:
                    print(f"{self.icons['continuation']}{self.icons['branch']}📝 {Colors.GRAY}{sequence['description']}{Colors.ENDC}")
                
                # Show progress
                print(f"{self.icons['continuation']}{self.icons['branch']}📊 Progress: {progress} ({percentage}%)")
                print(f"{self.icons['continuation']}{self.icons['branch']}{progress_bar}")
                
                # Show tasks in sequence
                for i, task in enumerate(sequence["tasks"]):
                    is_last = i == len(sequence["tasks"]) - 1
                    prefix = f"{self.icons['continuation']}{self.icons['last_branch'] if is_last else self.icons['branch']}"
                    
                    status_icon = self._get_status_icon(task["status"])
                    status_color = self._get_status_color(task["status"])
                    
                    print(f"{prefix}{status_color}{status_icon}Task {i+1}: {task['description']}{Colors.ENDC}")
                
                print()
        
        # Display processing queue
        if task_tree["processing_queue"]:
            print(f"{Colors.BOLD}⏳ PROCESSING QUEUE ({len(task_tree['processing_queue'])} tasks){Colors.ENDC}")
            for i, task in enumerate(task_tree["processing_queue"]):
                is_last = i == len(task_tree["processing_queue"]) - 1
                prefix = self.icons['last_branch'] if is_last else self.icons['branch']
                
                priority_color = self._get_priority_color(task["priority"])
                priority_icon = self._get_priority_icon(task["priority"])
                status_icon = self._get_status_icon(task["status"])
                status_color = self._get_status_color(task["status"])
                
                age_info = f" ({task['age']})" if task["age"] else ""
                
                print(f"{priority_color}{prefix}{priority_icon}{status_color}{status_icon}{task['description']}{age_info}{Colors.ENDC}")
                
                # Display subtasks if any
                if task["subtasks"]:
                    subtask_prefix = self.icons['empty'] if is_last else self.icons['continuation']
                    for j, subtask in enumerate(task["subtasks"]):
                        is_last_subtask = j == len(task["subtasks"]) - 1
                        subtask_branch = self.icons['last_branch'] if is_last_subtask else self.icons['branch']
                        subtask_status = subtask.get("status", "pending")
                        subtask_status_color = self._get_status_color(subtask_status)
                        subtask_status_icon = self._get_status_icon(subtask_status)
                        
                        print(f"{subtask_prefix}{subtask_branch}{subtask_status_color}{subtask_status_icon}{subtask.get('description', 'No description')}{Colors.ENDC}")
            
            print()
        
        # Display constant tasks
        if task_tree["constant_tasks"]:
            print(f"{Colors.BOLD}🔄 CONSTANT TASKS ({len(task_tree['constant_tasks'])} tasks){Colors.ENDC}")
            for i, task in enumerate(task_tree["constant_tasks"]):
                is_last = i == len(task_tree["constant_tasks"]) - 1
                prefix = self.icons['last_branch'] if is_last else self.icons['branch']
                
                priority_color = self._get_priority_color(task["priority"])
                priority_icon = self._get_priority_icon(task["priority"])
                
                interval = task.get("interval", "every_cycle")
                print(f"{priority_color}{prefix}{priority_icon}{task['description']} {Colors.GRAY}[{interval}]{Colors.ENDC}")
            
            print()
        
        # Display next cycle plan
        if task_tree["next_cycle_plan"]:
            print(f"{Colors.BOLD}📅 NEXT CYCLE PLAN ({len(task_tree['next_cycle_plan'])} tasks){Colors.ENDC}")
            for i, task in enumerate(task_tree["next_cycle_plan"]):
                is_last = i == len(task_tree["next_cycle_plan"]) - 1
                prefix = self.icons['last_branch'] if is_last else self.icons['branch']
                
                priority_color = self._get_priority_color(task["priority"])
                priority_icon = self._get_priority_icon(task["priority"])
                
                print(f"{priority_color}{prefix}{priority_icon}{task['description']}{Colors.ENDC}")
            
            print()
        
        # If no tasks found
        if not any(task_tree.values()):
            print(f"{Colors.GRAY}No tasks currently in the system.{Colors.ENDC}")
    
    def _get_priority_color(self, priority):
        """Get color based on priority level"""
        if priority.lower() == "high":
            return Colors.HIGH
        elif priority.lower() == "medium":
            return Colors.MEDIUM
        else:
            return Colors.LOW
    
    def _get_priority_icon(self, priority):
        """Get icon based on priority level"""
        if priority.lower() == "high":
            return self.icons["high_priority"]
        elif priority.lower() == "medium":
            return self.icons["medium_priority"]
        else:
            return self.icons["low_priority"]
    
    def _get_status_color(self, status):
        """Get color based on task status"""
        if status.lower() == "completed":
            return Colors.COMPLETED
        elif status.lower() == "in_progress":
            return Colors.IN_PROGRESS
        elif status.lower() == "failed":
            return Colors.FAILED
        else:
            return Colors.PENDING
    
    def _get_status_icon(self, status):
        """Get icon based on task status"""
        if status.lower() == "completed":
            return self.icons["completed"]
        elif status.lower() == "in_progress":
            return self.icons["in_progress"]
        elif status.lower() == "failed":
            return self.icons["failed"]
        else:
            return self.icons["pending"]
    
    def _create_progress_bar(self, percentage, length=30):
        """Create a visual progress bar"""
        filled_length = int(length * percentage // 100)
        empty_length = length - filled_length
        
        # Color-code based on percentage
        if percentage < 30:
            color = Colors.RED
        elif percentage < 70:
            color = Colors.YELLOW
        else:
            color = Colors.GREEN
            
        bar = f"{color}{'█' * filled_length}{Colors.GRAY}{'░' * empty_length}{Colors.ENDC}"
        return f"[{bar}] {percentage}%"
    
    def _display_subtasks(self, subtasks, parent_prefix_base):
        """Helper method to display a list of subtasks"""
        for j, subtask_item in enumerate(subtasks):
            is_last_subtask = j == len(subtasks) - 1
            subtask_branch = self.icons['last_branch'] if is_last_subtask else self.icons['branch']
            
            subtask_status = subtask_item.get("status", "pending")
            subtask_status_color = self._get_status_color(subtask_status)
            subtask_status_icon = self._get_status_icon(subtask_status)
            
            print(f"{parent_prefix_base}{subtask_branch}{subtask_status_color}{subtask_status_icon}{subtask_item.get('description', 'No description')}{Colors.ENDC}")
    
    def _write_to_log(self, data):
        """Write task tree data to log file"""
        try:
            with open(TASK_TREE_LOG, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"{Colors.RED}Error writing to log file: {e}{Colors.ENDC}")
    
    def run(self):
        """Run the task tree window"""
        self.print_header()
        
        try:
            # Initial display
            self.display_task_tree()
            
            while not self.thread_stop_event.is_set():
                # Wait a bit
                time.sleep(2)
                
                # Periodically refresh
                current_time = time.time()
                if current_time - self.last_check_time >= 3:  # Refresh every 3 seconds
                    self.print_header()
                    self.display_task_tree()
                    self.last_check_time = current_time
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Exiting task tree window...{Colors.ENDC}")
        finally:
            self.thread_stop_event.set()

if __name__ == "__main__":
    window = TaskTreeWindow()
    window.run()
