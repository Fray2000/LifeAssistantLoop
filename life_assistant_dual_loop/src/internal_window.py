#!/usr/bin/env python3
# filepath: c:\Users\francesc.leo\Documents\gitlab\LifeAssistantLoop\internal_window.py

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import time
import json
import datetime
import threading
import queue
import re
import random

# Define colors for different thought types
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
    ORANGE = '\033[38;5;208m'  # Added for multi-cycle tasks

# Path definitions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_BACKEND_DIR = os.path.join(BASE_DIR, 'data-backend')
THOUGHTS_FILE = os.path.join(DATA_BACKEND_DIR, 'internal_thoughts.log')
THREAD_STOP_EVENT = threading.Event()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the window header"""
    clear_screen()
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}🧠 BACKEND INTERNAL THOUGHTS WINDOW 🧠{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.PURPLE}This window displays the AI's internal reasoning process, memory operations,")
    print(f"and task management. You can see what's happening behind the scenes in real-time.{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
def format_thought(line):
    """Format a thought line with proper colors"""
    # Example line: [14:30:45] THINKING: Analyzing user request
    pattern = r'\[(.*?)\] ([A-Z]+): (.*)'
    match = re.match(pattern, line)
    
    if match:
        timestamp, thought_type, content = match.groups()
          # Color mapping for different thought types
        color_map = {
            'THINKING': Colors.CYAN,
            'ACTION': Colors.YELLOW,
            'MEMORY': Colors.GREEN,
            'TASK': Colors.PURPLE,
            'ERROR': Colors.RED,
            'SUCCESS': Colors.BLUE,
            'DEBUG': Colors.GRAY,
            'MULTI_TASK': Colors.ORANGE,  # Added for multi-cycle tasks
            'SEQUENCE': Colors.BLUE       # Added for task sequences
        }
        
        color = color_map.get(thought_type, Colors.ENDC)
        
        # Format the output nicely
        return f"{Colors.GRAY}[{timestamp}]{Colors.ENDC} {color}{thought_type}:{Colors.ENDC} {content}"
    
    return line

def watch_thoughts_file():
    """Monitor the thoughts file for new entries"""
    if not os.path.exists(THOUGHTS_FILE):
        # Create the file if it doesn't exist
        with open(THOUGHTS_FILE, 'w', encoding='utf-8') as f:
            f.write("")
    
    # Get the initial file size
    last_size = os.path.getsize(THOUGHTS_FILE)
    
    while not THREAD_STOP_EVENT.is_set():
        try:
            # Check if file size has changed
            current_size = os.path.getsize(THOUGHTS_FILE)
            
            if current_size > last_size:
                # Read the new content
                with open(THOUGHTS_FILE, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_content = f.read()
                
                # Process and print each new line
                for line in new_content.splitlines():
                    if line.strip():
                        formatted_line = format_thought(line)
                        print(formatted_line)
                
                # Update last size
                last_size = current_size
        except Exception as e:
            print(f"{Colors.RED}Error monitoring thoughts file: {e}{Colors.ENDC}")
        
        # Sleep briefly before checking again
        time.sleep(0.2)

def display_multi_cycle_status():
    """Display current status of multi-cycle tasks if any are active"""
    try:
        backend_memory_path = os.path.join(DATA_BACKEND_DIR, 'backend_memory.json')
        if os.path.exists(backend_memory_path):
            with open(backend_memory_path, 'r') as f:
                memory = json.load(f)
                
            multi_cycle = memory.get('multi_cycle_tasks', {})
            active_sequences = multi_cycle.get('active_sequences', {})
            current_id = multi_cycle.get('current_sequence_id')
            
            if current_id and current_id in active_sequences:
                sequence = active_sequences[current_id]
                name = sequence.get('name', 'Unknown')
                tasks = sequence.get('tasks', [])
                current_idx = sequence.get('current_task_index', 0)
                status = sequence.get('status', 'pending')
                
                print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*30} ACTIVE MULTI-CYCLE SEQUENCE {'='*30}{Colors.ENDC}")
                print(f"{Colors.ORANGE}Sequence: {name} ({status}){Colors.ENDC}")
                print(f"{Colors.ORANGE}Progress: Task {current_idx+1}/{len(tasks)} ({int((current_idx/len(tasks))*100)}%){Colors.ENDC}")
                
                # Show task list with status indicators
                print(f"{Colors.ORANGE}Tasks:{Colors.ENDC}")
                for i, task in enumerate(tasks):
                    if i < current_idx:
                        # Completed task
                        print(f"{Colors.GREEN}  ✓ {task}{Colors.ENDC}")
                    elif i == current_idx:
                        # Current task
                        print(f"{Colors.YELLOW}  ➤ {task} (CURRENT){Colors.ENDC}")
                    else:
                        # Pending task
                        print(f"{Colors.GRAY}  ○ {task}{Colors.ENDC}")
                        
                print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.ENDC}\n")
                return True
    except Exception as e:
        print(f"{Colors.RED}Error displaying multi-cycle status: {e}{Colors.ENDC}")
    
    return False

def main():
    """Main function to run the internal window"""
    print_header()
    
    # Create watcher thread
    watcher_thread = threading.Thread(target=watch_thoughts_file, daemon=True)
    watcher_thread.start()
    
    # Keep the window alive until CTRL+C
    try:
        # Show active multi-cycle tasks if any
        display_multi_cycle_status()
        
        # Display periodic status updates
        last_status_check = time.time()
        # Add current status info
        if os.path.exists(THOUGHTS_FILE):
            with open(THOUGHTS_FILE, 'r', encoding='utf-8') as f:
                # Get last 10 lines of history
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                
                if recent_lines:
                    print(f"{Colors.GRAY}--- Recent activity ---{Colors.ENDC}")
                    for line in recent_lines:
                        print(format_thought(line.strip()))
                    print()
        
        print(f"{Colors.GREEN}Monitoring for internal thoughts... Press Ctrl+C to exit.{Colors.ENDC}")
          # Watch for CTRL+C and periodically refresh multi-cycle task status
        while True:
            current_time = time.time()
            
            # Check for multi-cycle task updates every 5 seconds
            if current_time - last_status_check > 5:
                # Clear screen occasionally to prevent overcrowding
                if random.random() < 0.2:  # 20% chance of clearing and full refresh
                    print_header()
                    display_multi_cycle_status()
                    # Show last few thought entries
                    if os.path.exists(THOUGHTS_FILE):
                        with open(THOUGHTS_FILE, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            recent_lines = lines[-5:] if len(lines) > 5 else lines
                            if recent_lines:
                                print(f"{Colors.GRAY}--- Recent activity ---{Colors.ENDC}")
                                for line in recent_lines:
                                    print(format_thought(line.strip()))
                else:
                    # Just check for multi-cycle task updates
                    display_multi_cycle_status()
                
                last_status_check = current_time
                
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting internal window...{Colors.ENDC}")
    finally:
        THREAD_STOP_EVENT.set()
        watcher_thread.join(timeout=1.0)

if __name__ == "__main__":
    main()
