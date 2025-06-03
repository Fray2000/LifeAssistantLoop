import os
import json
from .functions import FUNCTIONS

class FunctionExecutor:
    def __init__(self):
        pass
        
    def execute(self, action, editor, memory):
        # action: dict with 'type', 'args', etc.
        action_type = action.get('type')
        
        # Detailed debug message showing what action is being executed
        print(f"\n==== ACTION EXECUTION DETAILS ====")
        print(f"Action Type: {action_type}")
        print(f"Arguments: {json.dumps(action.get('args', {}), indent=2)}")
        print(f"===============================")
        
        if action_type in FUNCTIONS:
            result = FUNCTIONS[action_type](**action.get('args', {}))
            return result
        elif action_type == 'edit_markdown':
            file_path = action['args']['file']
            new_content = action['args']['content']
            
            # Resolve file path
            if not os.path.isabs(file_path):
                # Use BASE_DIR from run_agent.py
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(os.path.dirname(base_dir), file_path)
                
            print(f"DEBUG: Applying edit to file: {file_path}")
            editor.apply_edit(file_path, new_content)
            return f"Edited {file_path}"
        elif action_type == 'edit_file':
            file_path = action['args']['file']
            new_content = action['args']['content']
            
            # Resolve file path
            if not os.path.isabs(file_path):
                # Use BASE_DIR from run_agent.py
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(os.path.dirname(base_dir), file_path)
                
            editor.apply_edit(file_path, new_content)
            return f"Edited file {file_path}"        
        
        elif action_type == 'update_memory':
            memory.update(action['args'])
            return "Memory updated"
        
        elif action_type == 'add_task':
            task = action['args']['task']
            file_path = action['args'].get('file', 'src/tasks.md')
            # Resolve file path if it's relative
            if not os.path.isabs(file_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(base_dir, file_path)
            print(f"DEBUG: Adding task to file: {file_path}")
            tasks = editor.read_markdown(file_path)
            if '# Tasks' not in tasks:
                tasks = "# Tasks\n\n"
            if task not in tasks:
                tasks += f"- [ ] {task}\n"
                editor.apply_edit(file_path, tasks)
            return f"Added task: {task}"
        elif action_type == 'complete_task':
            task = action['args']['task']
            file_path = action['args'].get('file', 'src/tasks.md')
            # Resolve file path if it's relative
            if not os.path.isabs(file_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(base_dir, file_path)
            print(f"DEBUG: Completing task in file: {file_path}")
            tasks = editor.read_markdown(file_path)
            if f"- [ ] {task}" in tasks:
                tasks = tasks.replace(f"- [ ] {task}", f"- [x] {task}")
                editor.apply_edit(file_path, tasks)
                return f"Completed task: {task}"
            return f"Task not found: {task}"
        else:
            return f"Unknown action: {action_type}"
