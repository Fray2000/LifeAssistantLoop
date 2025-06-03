#!/usr/bin/env python3

import os
import json
import datetime
import sys

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.memory_manager import MemoryManager

# Path definitions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_USER_DIR = os.path.join(BASE_DIR, 'data-user')
DATA_BACKEND_DIR = os.path.join(BASE_DIR, 'data-backend')
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Memory files
USER_MEMORY = os.path.join(DATA_USER_DIR, 'memory.json')
BACKEND_MEMORY = os.path.join(DATA_BACKEND_DIR, 'backend_memory.json')
TASK_BUFFER_FILE = os.path.join(SRC_DIR, 'task_buffer.json')

def initialize_memory():
    """Reset and initialize all user and backend memory for a clean workspace."""
    print("Resetting and initializing split memory architecture...")

    # Ensure the directories exist
    os.makedirs(DATA_USER_DIR, exist_ok=True)
    os.makedirs(DATA_BACKEND_DIR, exist_ok=True)
    os.makedirs(SRC_DIR, exist_ok=True)

    # Create memory manager for user memory
    user_memory_manager = MemoryManager(USER_MEMORY)

    # Reset user memory with extended personal info
    user_memory_manager.update_user_memory({
        "personal": {
            "full_name": None,
            "birthdate": None,
            "age": None,
            "gender": None,
            "height": None,
            "weight": None,
            "health_conditions": [],
            "medications": [],
            "emergency_contacts": [],
            "address": None,
            "contracts": [],
            "insurance": {},
            "doctors": [],
            "friends": [],
            "family": [],
            "pets": [],
            "hobbies": []
        },
        "tasks": {
            "completed": [],
            "in_progress": [],
            "priorities": []
        },
        "knowledge": {
            "learned_patterns": {},
            "user_preferences": {},
            "important_dates": {},
            "subscriptions": [],
            "important_documents": [],
            "goals": [],
            "travel_history": [],
            "vehicles": []
        },
        "notes": [],
        "last_interaction": None
    })

    # Reset system memory (shared between frontend and backend)
    user_memory_manager.update_system_memory({
        "system": {
            "version": "2.0.0",
            "frontend_last_startup": None,
            "backend_last_startup": None,
            "cycles_completed": 0,
            "features_implemented": ["split-memory"]
        },
        "self_improvement": {
            "proposed_enhancements": [],
            "successful_changes": [],
            "failed_attempts": []
        },
        "internal_state": {
            "last_processed_request_id": None,
            "last_request_time": None
        },
        "technical_knowledge": {}
    })

    # Create memory manager for backend memory
    backend_memory_manager = MemoryManager(USER_MEMORY, BACKEND_MEMORY, is_backend=True)

    # Reset backend memory
    backend_memory_manager.update_backend_memory({
        "constant_tasks": [],
        "processing_queue": [],
        "execution_history": [],
        "backend_state": {
            "last_execution": None,
            "execution_count": 0,
            "active_tasks": []
        },
        "next_cycle_plan": []
    })

    # Reset task buffer
    with open(TASK_BUFFER_FILE, 'w') as f:
        json.dump([], f)
    # Clear backend request/response buffers
    backend_request = os.path.join(SRC_DIR, 'backend_request.json')
    backend_response = os.path.join(SRC_DIR, 'backend_response.json')
    for buffer_file in [backend_request, backend_response]:
        with open(buffer_file, 'w') as f:
            json.dump({"status": "cleared"}, f)
    print("All memory, tasks, and buffers have been reset!")
    print(f"User memory file reset at: {USER_MEMORY}")
    print(f"Backend memory file reset at: {BACKEND_MEMORY}")
    print(f"Task buffer file reset at: {TASK_BUFFER_FILE}")
    print(f"Backend request/response buffers cleared.")

if __name__ == "__main__":
    # Check if memory already exists
    if os.path.exists(USER_MEMORY) or os.path.exists(BACKEND_MEMORY):
        response = input(f"Memory files already exist. Overwrite? (y/n): ")
        if response.lower() == 'y':
            initialize_memory()
        else:
            print("Initialization cancelled.")
    else:
        initialize_memory()
