from .functions import FUNCTIONS

class FunctionExecutor:
    def __init__(self):
        pass

    def execute(self, action, editor, memory):
        # action: dict with 'type', 'args', etc.
        action_type = action.get('type')
        if action_type in FUNCTIONS:
            result = FUNCTIONS[action_type](**action.get('args', {}))
            return result
        elif action_type == 'edit_markdown':
            file_path = action['args']['file']
            new_content = action['args']['content']
            editor.apply_edit(file_path, new_content)
            return f"Edited {file_path}"
        elif action_type == 'edit_file':
            file_path = action['args']['file']
            new_content = action['args']['content']
            editor.apply_edit(file_path, new_content)
            return f"Edited file {file_path}"
        elif action_type == 'update_memory':
            memory.update(action['args'])
            return "Memory updated"
        elif action_type == 'add_task':
            task = action['args']['task']
            file_path = action['args'].get('file', 'src/tasks.md')
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
            tasks = editor.read_markdown(file_path)
            if f"- [ ] {task}" in tasks:
                tasks = tasks.replace(f"- [ ] {task}", f"- [x] {task}")
                editor.apply_edit(file_path, tasks)
                return f"Completed task: {task}"
            return f"Task not found: {task}"
        else:
            return f"Unknown action: {action_type}"
