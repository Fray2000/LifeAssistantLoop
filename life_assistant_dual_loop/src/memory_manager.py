import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import json
import datetime

class MemoryManager:
    """
    Manages the multi-memory system: user memory, system memory, and backend memory.
    Provides methods for accessing and updating all memory stores.
    """
    
    def __init__(self, memory_path, backend_memory_path=None, is_backend=False):
        self.memory_path = memory_path
        self.backend_memory_path = backend_memory_path
        self.is_backend = is_backend
        
        self.user_memory = {}
        self.system_memory = {}
        self.backend_memory = {}
        self.load_memory()
        
    def load_memory(self):
        """
        Load memory from files and split into user, system, and backend parts
        """
        try:
            # Load user-facing memory with new comprehensive structure
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'r') as f:
                    user_memory_data = json.load(f)
                    
                # Use the new comprehensive memory structure directly
                self.user_memory = user_memory_data
                
                # Extract system memory from the system_state section
                self.system_memory = {
                    "system_state": user_memory_data.get("system_state", {
                        "last_interaction_timestamp": datetime.datetime.now().isoformat(),
                        "active_mode": "assistant",
                        "current_focus": "general_assistance",
                        "system_version": "3.0.0"
                    }),
                    "assistant_memory": user_memory_data.get("assistant_memory", {
                        "conversation_history": [],
                        "learned_patterns": {},
                        "user_feedback": []
                    }),
                    "multi_cycle_tasks": {
                        "active_sequences": {},
                        "completed_sequences": {},
                        "current_sequence_id": None
                    }
                }
            else:
                # Initialize with new comprehensive structure
                self.user_memory = self._get_default_user_memory()
                self.system_memory = self._get_default_system_memory()
            
            # Load backend-specific memory if applicable
            if self.is_backend and self.backend_memory_path and os.path.exists(self.backend_memory_path):
                with open(self.backend_memory_path, 'r') as f:
                    self.backend_memory = json.load(f)
            elif self.is_backend:
                # Initialize default backend memory structure
                self.backend_memory = {
                    "constant_tasks": [],
                    "processing_queue": [],
                    "execution_history": [],
                    "backend_state": {
                        "last_execution": datetime.datetime.now().isoformat(),
                        "execution_count": 0,
                        "active_tasks": []
                    },
                    "next_cycle_plan": [],
                    "multi_cycle_tasks": {
                        "active_sequences": {},
                        "completed_sequences": {},
                        "current_sequence_id": None
                    }
                }
                
        except Exception as e:
            print(f"Error loading memory: {e}")
            # Set up default memory structures
            self.user_memory = self._get_default_user_memory()
            self.system_memory = self._get_default_system_memory()

    def _get_default_user_memory(self):
        """Get the default comprehensive user memory structure"""
        return {
            "personal_info": {
                "profile": {
                    "full_name": "",
                    "preferred_name": "",
                    "age": None,
                    "date_of_birth": ""
                },
                "contact": {
                    "phone": "",
                    "email": "",
                    "address": ""
                },
                "appearance": {
                    "height": "",
                    "weight": ""
                },
                "preferences": {
                    "communication_style": "",
                    "interests": [],
                    "goals": []
                }
            },
            "health_and_wellness": {
                "medical_conditions": [],
                "medications": [],
                "doctors": {},
                "fitness": {
                    "goals": [],
                    "activities": []
                },
                "diet": {
                    "restrictions": [],
                    "preferences": []
                },
                "mental_health": {
                    "mood_tracking": [],
                    "stress_management": []
                }
            },
            "calendar_and_events": {
                "events": [],
                "reminders": [],
                "availability": {}
            },
            "finance_and_banking": {
                "accounts": {},
                "transactions": [],
                "budgets": {},
                "bills": [],
                "investments": {},
                "contracts": []
            },
            "social_and_relationships": {
                "contacts": {
                    "friends": [],
                    "family": {},
                    "colleagues": []
                },
                "social_events": [],
                "friend_groups": {}
            },
            "work_and_projects": {
                "current_job": {},
                "projects": [],
                "tasks": [],
                "completed_tasks": [],
                "goals": [],
                "documents": []
            },
            "knowledge_and_learning": {
                "skills": [],
                "education": {},
                "courses": [],
                "certifications": [],
                "travel": {
                    "places_visited": [],
                    "travel_plans": []
                },
                "vehicles": [],
                "subscriptions": []
            },
            "devices_and_smart_home": {
                "devices": {},
                "smart_home_routines": []
            },
            "system_state": {
                "last_interaction_timestamp": datetime.datetime.now().isoformat(),
                "active_mode": "assistant",
                "current_focus": "general_assistance"
            },
            "assistant_memory": {
                "conversation_history": [],
                "learned_patterns": {},
                "user_feedback": []
            }
        }

    def _get_default_system_memory(self):
        """Get the default system memory structure"""
        return {
            "system_state": {
                "last_interaction_timestamp": datetime.datetime.now().isoformat(),
                "active_mode": "assistant",
                "current_focus": "general_assistance",
                "system_version": "3.0.0"
            },
            "assistant_memory": {
                "conversation_history": [],
                "learned_patterns": {},            "user_feedback": []
            },
            "multi_cycle_tasks": {                "active_sequences": {},
                "completed_sequences": {},
                "current_sequence_id": None
            }
        }

    def save_memory(self):
        """
        Save all memory stores to their respective files
        """
        try:
            # Save comprehensive user memory directly (no more combining needed)
            # Update system_state timestamp
            self.user_memory.setdefault("system_state", {})["last_interaction_timestamp"] = datetime.datetime.now().isoformat()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            with open(self.memory_path, 'w') as f:
                json.dump(self.user_memory, f, indent=2)
            
            # Save backend memory if applicable
            if self.is_backend and self.backend_memory_path:
                # Update backend state timestamp
                self.backend_memory.setdefault("backend_state", {})["last_execution"] = datetime.datetime.now().isoformat()
                
                os.makedirs(os.path.dirname(self.backend_memory_path), exist_ok=True)
                with open(self.backend_memory_path, 'w') as f:
                    json.dump(self.backend_memory, f, indent=2)
                    
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def update_user_memory(self, updates):
        """
        Update the user-facing memory with new data
        """
        for key, value in updates.items():
            if isinstance(value, dict) and key in self.user_memory and isinstance(self.user_memory[key], dict):
                # Deep merge for nested dictionaries
                self._deep_update(self.user_memory[key], value)
            else:
                # Direct update for non-dictionary values
                self.user_memory[key] = value
        
        # Save memory after updating
        self.save_memory()
    
    def update_system_memory(self, updates):
        """
        Update the system memory with new data
        """
        for key, value in updates.items():
            if isinstance(value, dict) and key in self.system_memory and isinstance(self.system_memory[key], dict):
                # Deep merge for nested dictionaries
                self._deep_update(self.system_memory[key], value)
            else:
                # Direct update for non-dictionary values
                self.system_memory[key] = value
        
        # Save memory after updating
        self.save_memory()
    
    def update_backend_memory(self, updates):
        """
        Update the backend-specific memory with new data
        """
        if not self.is_backend:
            print("Warning: Attempting to update backend memory from frontend component")
            return
            
        for key, value in updates.items():
            if isinstance(value, dict) and key in self.backend_memory and isinstance(self.backend_memory[key], dict):
                # Deep merge for nested dictionaries
                self._deep_update(self.backend_memory[key], value)
            else:
                # Direct update for non-dictionary values
                self.backend_memory[key] = value
        
        # Save memory after updating
        self.save_memory()
    
    def get_user_memory(self):
        """
        Get the user-facing memory
        """
        return self.user_memory
    
    def get_system_memory(self):
        """
        Get the system memory
        """
        return self.system_memory
    
    def get_backend_memory(self):
        """
        Get the backend-specific memory
        """
        if not self.is_backend:
            print("Warning: Attempting to access backend memory from frontend component")
        return self.backend_memory
    
    def add_to_processing_queue(self, task):
        """
        Add a task to the backend processing queue
        """
        if not self.is_backend:
            print("Warning: Attempting to update backend queue from frontend component")
            return
            
        if "processing_queue" not in self.backend_memory:
            self.backend_memory["processing_queue"] = []
            
        self.backend_memory["processing_queue"].append({
            "task": task,
            "added_at": datetime.datetime.now().isoformat(),
            "status": "pending"
        })
        
        self.save_memory()
        
    def get_next_task_from_queue(self):
        """
        Get the next task from the processing queue
        """
        if not self.is_backend:
            print("Warning: Attempting to access backend queue from frontend component")
            
        if "processing_queue" in self.backend_memory and self.backend_memory["processing_queue"]:
            # Find the first pending task
            for i, task in enumerate(self.backend_memory["processing_queue"]):
                if task["status"] == "pending":
                    # Mark as in-progress
                    self.backend_memory["processing_queue"][i]["status"] = "in_progress"
                    self.backend_memory["processing_queue"][i]["started_at"] = datetime.datetime.now().isoformat()
                    self.save_memory()
                    return task["task"]
        
        return None
        
    def mark_task_complete(self, task_index, result):
        """
        Mark a task in the processing queue as complete
        """
        if not self.is_backend:
            print("Warning: Attempting to update backend queue from frontend component")
            return
            
        if ("processing_queue" in self.backend_memory and 
            0 <= task_index < len(self.backend_memory["processing_queue"])):
            
            self.backend_memory["processing_queue"][task_index]["status"] = "completed"
            self.backend_memory["processing_queue"][task_index]["completed_at"] = datetime.datetime.now().isoformat()
            self.backend_memory["processing_queue"][task_index]["result"] = result
            
            # Move to execution history
            if "execution_history" not in self.backend_memory:
                self.backend_memory["execution_history"] = []
                
            self.backend_memory["execution_history"].append(self.backend_memory["processing_queue"][task_index])
            
            # Update state
            if "backend_state" not in self.backend_memory:
                self.backend_memory["backend_state"] = {}
                
            self.backend_memory["backend_state"]["last_execution"] = datetime.datetime.now().isoformat()
            self.backend_memory["backend_state"]["execution_count"] = self.backend_memory["backend_state"].get("execution_count", 0) + 1
            
            self.save_memory()
            
    def add_constant_task(self, task):
        """
        Add a constant task to the backend
        """
        if not self.is_backend:
            print("Warning: Attempting to update backend tasks from frontend component")
            return
            
        if "constant_tasks" not in self.backend_memory:
            self.backend_memory["constant_tasks"] = []
            
        # Check if task already exists
        for existing_task in self.backend_memory["constant_tasks"]:
            if existing_task.get("description") == task.get("description"):
                return  # Task already exists
                
        self.backend_memory["constant_tasks"].append({
            "description": task.get("description"),
            "interval": task.get("interval", "every_cycle"),  # How often to run
            "priority": task.get("priority", "medium"),
            "added_at": datetime.datetime.now().isoformat(),
            "last_executed": None
        })
        
        self.save_memory()
        
    def get_due_constant_tasks(self):
        """
        Get constant tasks that are due for execution
        """
        if not self.is_backend:
            print("Warning: Attempting to access backend tasks from frontend component")
            
        if "constant_tasks" not in self.backend_memory:
            return []
            
        now = datetime.datetime.now()
        due_tasks = []
        
        for task in self.backend_memory["constant_tasks"]:
            # Default: execute every cycle
            should_execute = True
            
            # Check intervals
            if task["interval"] != "every_cycle":
                last_executed = task.get("last_executed")
                if last_executed:
                    last_time = datetime.datetime.fromisoformat(last_executed)
                    
                    # Check different intervals
                    if task["interval"] == "hourly" and (now - last_time).seconds < 3600:
                        should_execute = False
                    elif task["interval"] == "daily" and (now - last_time).days < 1:
                        should_execute = False
                    elif task["interval"] == "weekly" and (now - last_time).days < 7:
                        should_execute = False
            
            if should_execute:
                due_tasks.append(task)
                
        return due_tasks
    
    def _deep_update(self, d, u):
        """
        Helper method for deep dictionary updates
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
