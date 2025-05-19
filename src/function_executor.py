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
        elif action_type == 'update_memory':
            memory.update(action['args'])
            return "Memory updated"
        else:
            return f"Unknown action: {action_type}"
