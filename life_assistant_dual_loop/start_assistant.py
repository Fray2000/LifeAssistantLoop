#!/usr/bin/env python3

import sys
import subprocess
import os
import time
import platform
import signal
import argparse

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Start the Life Assistant system")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--backend-only", action="store_true", help="Start only the backend component")
    parser.add_argument("--frontend-only", action="store_true", help="Start only the frontend component")
    return parser.parse_args()

def ensure_directories_exist():
    """Make sure required directories exist"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create necessary directories
    dirs = [
        os.path.join(base_dir, 'data-user'),
        os.path.join(base_dir, 'data-backend'),
        os.path.join(base_dir, 'logs'),
        os.path.join(base_dir, 'src')
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        
    # Create task_buffer.json if it doesn't exist
    task_buffer = os.path.join(base_dir, 'src', 'task_buffer.json')
    if not os.path.exists(task_buffer):
        with open(task_buffer, 'w') as f:
            f.write('[]')
            
    print("Directory structure verified.")

def start_life_assistant():
    """Start the Life Assistant system (both frontend and backend components)"""
    args = parse_args()
    print("Starting Life Assistant System...")
    ensure_directories_exist()
      # Determine how to open new terminals based on the platform
    if platform.system() == "Windows":
        # On Windows, use start cmd
        if not args.frontend_only:
            backend_command = "start cmd /k python src/backend_loop.py"
            if args.debug:
                backend_command += " --debug"
            print("Starting backend in a new window...")
            subprocess.Popen(backend_command, shell=True)
            time.sleep(1)
            
            # Start task tree visualization
            task_tree_command = "start cmd /k python src/task_tree_window.py"
            print("Starting task tree visualization in a new window...")
            subprocess.Popen(task_tree_command, shell=True)
            time.sleep(1)
            
            # Start internal window for backend thoughts
            internal_window_command = "start cmd /k python src/internal_window.py"
            print("Starting internal window in a new window...")
            subprocess.Popen(internal_window_command, shell=True)
            time.sleep(1)
            
        if not args.backend_only:
            frontend_command = "start cmd /k python src/frontend_assistant.py"
            if args.debug:
                frontend_command += " --debug"
            print("Starting frontend in a new window...")
            subprocess.Popen(frontend_command, shell=True)
            time.sleep(1)
        # Log viewer window
        log_command = (
            'start cmd /k powershell -NoExit -Command "Get-Content -Path .\\data-backend\\change_log.md, .\\data-backend\\backend_log.md -Wait"'
        )
        print("Starting log viewer in a new window...")
        subprocess.Popen(log_command, shell=True)
        # Main process can exit or wait
        print("All windows started. You can close this window.")
        return
    
    elif platform.system() == "Darwin":  # macOS
        # On macOS, use osascript to open a new Terminal window
        if not args.frontend_only:
            backend_cmd = "python3 src/backend_loop.py"
            if args.debug:
                backend_cmd += " --debug"
            # Escape double quotes for AppleScript
            backend_cmd = backend_cmd.replace('"', '\\"')
            osascript_command = f'''
            osascript -e 'tell app "Terminal"
                do script "cd {os.getcwd()} && {backend_cmd}"
                set custom title of first window to "Life Assistant Backend"
            end tell'
            '''
            print("Starting backend in a new Terminal window...")
            subprocess.run(osascript_command, shell=True)
            time.sleep(2)  # Give it time to start
            # Start task tree visualization
            task_tree_cmd = "python3 src/task_tree_window.py"
            task_tree_cmd = task_tree_cmd.replace('"', '\\"')
            osascript_command = f'''
            osascript -e 'tell app "Terminal"
                do script "cd {os.getcwd()} && {task_tree_cmd}"
                set custom title of first window to "Task Tree Visualization"
            end tell'
            '''
            print("Starting task tree visualization in a new Terminal window...")
            subprocess.run(osascript_command, shell=True)
            time.sleep(2)  # Give it time to start
            # Start internal window for backend thoughts
            internal_window_cmd = "python3 src/internal_window.py"
            internal_window_cmd = internal_window_cmd.replace('"', '\\"')
            osascript_command = f'''
            osascript -e 'tell app "Terminal"
                do script "cd {os.getcwd()} && {internal_window_cmd}"
                set custom title of first window to "Internal Thoughts"
            end tell'
            '''
            print("Starting internal window in a new Terminal window...")
            subprocess.run(osascript_command, shell=True)
            time.sleep(2)  # Give it time to start
        if not args.backend_only:
            frontend_command = "python3 src/frontend_assistant.py"
            if args.debug:
                frontend_command += " --debug"
            # Start the frontend in the current terminal
            print("Starting frontend...")
            os.system(frontend_command)

    else:  # Linux and other Unix-like systems
        # On Linux, use xterm or gnome-terminal based on what's available
        if not args.frontend_only:
            backend_started = False
            if os.system("which gnome-terminal > /dev/null 2>&1") == 0:
                backend_command = f"gnome-terminal -- bash -c 'cd {os.getcwd()} && python3 src/backend_loop.py"
                if args.debug:
                    backend_command += " --debug"
                backend_command += "; exec bash'"
                print("Starting backend in a new gnome-terminal window...")
                subprocess.run(backend_command, shell=True)
                backend_started = True
                # Start task tree visualization
                task_tree_command = f"gnome-terminal -- bash -c 'cd {os.getcwd()} && python3 src/task_tree_window.py; exec bash'"
                print("Starting task tree visualization in a new gnome-terminal window...")
                subprocess.run(task_tree_command, shell=True)
                # Start internal window
                internal_window_command = f"gnome-terminal -- bash -c 'cd {os.getcwd()} && python3 src/internal_window.py; exec bash'"
                print("Starting internal window in a new gnome-terminal window...")
                subprocess.run(internal_window_command, shell=True)
            elif os.system("which xterm > /dev/null 2>&1") == 0:
                backend_command = f"xterm -T 'Life Assistant Backend' -e 'cd {os.getcwd()} && python3 src/backend_loop.py"
                if args.debug:
                    backend_command += " --debug"
                backend_command += "; exec bash'"
                print("Starting backend in a new xterm window...")
                subprocess.run(backend_command, shell=True)
                backend_started = True
                # Start task tree visualization
                task_tree_command = f"xterm -T 'Task Tree Visualization' -e 'cd {os.getcwd()} && python3 src/task_tree_window.py; exec bash'"
                print("Starting task tree visualization in a new xterm window...")
                subprocess.run(task_tree_command, shell=True)
                # Start internal window
                internal_window_command = f"xterm -T 'Internal Thoughts' -e 'cd {os.getcwd()} && python3 src/internal_window.py; exec bash'"
                print("Starting internal window in a new xterm window...")
                subprocess.run(internal_window_command, shell=True)
            else:
                print("Could not find a suitable terminal emulator. Please start the backend manually in another terminal:")
                print(f"  python3 src/backend_loop.py {'--debug' if args.debug else ''}")
                print("  python3 src/task_tree_window.py")
                print("  python3 src/internal_window.py")
            if backend_started:
                time.sleep(2)  # Give it time to start
        if not args.backend_only:
            frontend_command = "python3 src/frontend_assistant.py"
            if args.debug:
                frontend_command += " --debug"
            # Start the frontend in the current terminal
            print("Starting frontend...")
            os.system(frontend_command)

if __name__ == "__main__":
    try:
        start_life_assistant()
    except KeyboardInterrupt:
        print("\nExiting Life Assistant startup script...")
    except Exception as e:
        print(f"Error starting Life Assistant: {e}")
        sys.exit(1)
