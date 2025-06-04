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
    user_memory_manager = MemoryManager(USER_MEMORY)    # Reset user memory with comprehensive schema
    user_memory_manager.update_user_memory({
        "personal_info": {
            "profile": {
                "full_name": None,
                "nicknames": [],
                "date_of_birth": None,
                "age": None,
                "gender": None,
                "pronouns": None,
                "languages_spoken": ["English"]
            },
            "contact": {
                "email_addresses": [],
                "phone_numbers": [],
                "mailing_address": {
                    "street": None,
                    "city": None,
                    "state_province": None,
                    "postal_code": None,
                    "country": None
                },
                "emergency_contacts": []
            },
            "appearance": {
                "height": None,
                "weight": None,
                "eye_color": None,
                "hair_color": None
            },
            "preferences": {
                "communication_style": "direct",
                "theme": "dark",
                "notification_preferences": {
                    "email": True,
                    "sms": False,
                    "push": True
                },
                "privacy_settings": {
                    "data_sharing": "minimal",
                    "anonymize_data": True
                }
            }
        },
        "health_and_wellness": {
            "medical_conditions": [],
            "allergies_sensitivities": [],
            "medications": [],
            "doctors_specialists": [],
            "insurance_information": [],
            "fitness": {
                "activity_log": [],
                "goals": [],
                "preferred_activities": [],
                "wearable_device_id": None
            },
            "diet_nutrition": {
                "dietary_restrictions": [],
                "preferences": [],
                "meal_log": [],
                "water_intake_goal_ml": 2000
            },
            "mental_health": {
                "mood_log": [],
                "stress_triggers": [],
                "coping_mechanisms": [],
                "therapist_id": None
            }
        },
        "calendar_and_events": {
            "events": [],
            "reminders": [],
            "availability_preferences": {
                "working_hours": {"start": "09:00", "end": "17:00", "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
                "preferred_meeting_times": ["10:00-12:00", "14:00-16:00"]
            }
        },
        "finance_and_banking": {
            "accounts": [],
            "transactions_log": [],
            "budgets": [],
            "bills_and_subscriptions": [],
            "investments": [],
            "financial_goals": [],
            "contracts_and_agreements": []
        },
        "social_and_relationships": {
            "contacts": [],
            "family_members": [],
            "friend_groups": [],
            "social_events_log": []
        },
        "work_and_projects": {
            "current_job": {
                "company_name": None,
                "job_title": None,
                "start_date": None,
                "manager_id": None,
                "team_members_ids": []
            },
            "projects": [],
            "tasks": {
                "pending": [],
                "in_progress": [],
                "completed": [],
                "priorities": {}
            },
            "goals_objectives": [],
            "notes_and_documents": []
        },
        "knowledge_and_learning": {
            "learned_topics": [],
            "areas_of_interest": [],
            "skills": [],
            "educational_background": [],
            "online_courses": [],
            "reading_list": [],
            "user_preferences_general": {},
            "important_dates_custom": [],
            "subscriptions_services": [],
            "travel_history_and_plans": [],
            "vehicles_and_transport": []
        },
        "devices_and_smart_home": {
            "devices": [],
            "smart_home_routines": []
        },
        "system_state": {
            "last_interaction_timestamp": None,
            "active_mode": "normal",
            "current_focus_task_id": None
        },
        "assistant_memory": {
            "conversation_history_summary": [],
            "learned_user_patterns": [],
            "feedback_log": []
        }
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
    backend_memory_manager = MemoryManager(USER_MEMORY, BACKEND_MEMORY, is_backend=True)    # Reset backend memory
    backend_memory_manager.update_backend_memory({
        "constant_tasks": [],
        "processing_queue": [],
        "execution_history": [],
        "backend_state": {
            "last_execution": None,
            "execution_count": 0,
            "active_tasks": []
        },
        "next_cycle_plan": [],
        "multi_cycle_tasks": {
            "active_sequences": [],
            "completed_sequences": [],
            "current_sequence_id": None
        }
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
