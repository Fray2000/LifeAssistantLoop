import os
import json
from .functions import FUNCTIONS

class FunctionExecutor:
    def __init__(self):
        pass
        
    def execute(self, action, editor, memory_manager):
        """Execute a user action with appropriate function"""
        action_type = action.get('type')
        args = action.get('args', {})
        
        # Basic built-in actions
        if action_type in FUNCTIONS:
            result = FUNCTIONS[action_type](**args)
            return result
            
        elif action_type == 'edit_markdown':
            file_path = self._resolve_path(args['file'])
            new_content = args['content']
            editor.apply_edit(file_path, new_content)
            return f"Updated {os.path.basename(file_path)}"
            
        elif action_type == 'add_task':
            task = args['task']
            file_path = self._resolve_path(args.get('file', 'src/tasks.md'))
            
            # Read current tasks
            tasks = editor.read_markdown(file_path)
            if '# Tasks' not in tasks:
                tasks = "# Tasks\n\n"
                
            # Add task if it doesn't exist
            if f"- [ ] {task}" not in tasks:
                tasks += f"- [ ] {task}\n"
                editor.apply_edit(file_path, tasks)
                
                # Also update memory
                memory_manager.update_user_memory({
                    "tasks": {
                        "in_progress": [task]
                    }
                })
                
            return f"Added task: {task}"
            
        elif action_type == 'complete_task':
            task = args['task']
            file_path = self._resolve_path(args.get('file', 'src/tasks.md'))
            
            tasks = editor.read_markdown(file_path)
            if f"- [ ] {task}" in tasks:
                tasks = tasks.replace(f"- [ ] {task}", f"- [x] {task}")
                editor.apply_edit(file_path, tasks)
                
                # Update user memory
                current_completed = memory_manager.get_user_memory().get("tasks", {}).get("completed", [])
                if task not in current_completed:
                    memory_manager.update_user_memory({
                        "tasks": {
                            "completed": current_completed + [task]
                        }
                    })
                    
                return f"Completed task: {task}"
                
            return f"Task not found: {task}"
            
        elif action_type == 'list_tasks':
            file_path = self._resolve_path(args.get('file', 'src/tasks.md'))
            tasks = editor.read_markdown(file_path)
            return {"tasks": tasks}
            
        elif action_type == 'remember':
            # Store information in user memory
            key = args.get('key')
            value = args.get('value')
            
            if key:
                memory_update = {}
                memory_update[key] = value
                memory_manager.update_user_memory(memory_update)
                return f"Remembered information under '{key}'"
            else:
                return "Error: No key provided for remember action"
                
        elif action_type == 'update_memory':
            # Enhanced: Support dot notation and top-level keys for new schema, for all info
            key = args.get('key')
            value = args.get('value')
            memory_type = args.get('memory_type', 'user')
            if memory_type == 'user' and key:
                user_mem = memory_manager.get_user_memory()
                # Support dot notation (e.g., personal.full_name)
                if '.' in key:
                    parts = key.split('.')
                    curr = user_mem
                    for p in parts[:-1]:
                        curr = curr.setdefault(p, {})
                    curr[parts[-1]] = value
                else:
                    # Try to match to personal/knowledge/tasks if key exists, else always add to personal
                    if key in user_mem.get('personal', {}):
                        user_mem['personal'][key] = value
                    elif key in user_mem.get('knowledge', {}):
                        user_mem['knowledge'][key] = value
                    elif key in user_mem.get('tasks', {}):
                        user_mem['tasks'][key] = value
                    else:
                        # Always add to personal if not found elsewhere
                        user_mem.setdefault('personal', {})[key] = value
                memory_manager.update_user_memory(user_mem)
                return f"User memory updated: {key} = {value}"
            elif memory_type == 'system' and key:
                # Similar logic for system memory if needed
                system_mem = memory_manager.get_system_memory()
                if '.' in key:
                    parts = key.split('.')
                    curr = system_mem
                    for p in parts[:-1]:
                        curr = curr.setdefault(p, {})
                    curr[parts[-1]] = value
                else:
                    system_mem[key] = value
                memory_manager.update_system_memory(system_mem)
                return f"System memory updated: {key} = {value}"
            else:
                memory_manager.update_user_memory(args)
                return "Memory updated"
        
        elif action_type == 'append_to_list':
            # Append a value to a list in user memory (e.g., friends, contracts)
            key = args.get('key')
            value = args.get('value')
            if key and value is not None:
                user_mem = memory_manager.get_user_memory()
                # Support nested keys like 'personal.friends'
                parts = key.split('.')
                curr = user_mem
                for p in parts[:-1]:
                    curr = curr.setdefault(p, {})
                lst = curr.setdefault(parts[-1], [])
                if value not in lst:
                    lst.append(value)
                    memory_manager.update_user_memory(user_mem)
                    return f"Appended {value} to {key}"
                else:
                    return f"Value {value} already in {key}"
            return "Error: key and value required for append_to_list"

        elif action_type == 'remove_from_list':
            # Remove a value from a list in user memory
            key = args.get('key')
            value = args.get('value')
            if key and value is not None:
                user_mem = memory_manager.get_user_memory()
                parts = key.split('.')
                curr = user_mem
                for p in parts[:-1]:
                    curr = curr.setdefault(p, {})
                lst = curr.setdefault(parts[-1], [])
                if value in lst:
                    lst.remove(value)
                    memory_manager.update_user_memory(user_mem)
                    return f"Removed {value} from {key}"
                else:
                    return f"Value {value} not found in {key}"
            return "Error: key and value required for remove_from_list"

        elif action_type == 'update_nested':
            # Update a nested field in user memory (e.g., insurance.policy_number)
            key = args.get('key')
            value = args.get('value')
            if key and value is not None:
                user_mem = memory_manager.get_user_memory()
                parts = key.split('.')
                curr = user_mem
                for p in parts[:-1]:
                    curr = curr.setdefault(p, {})
                curr[parts[-1]] = value
                memory_manager.update_user_memory(user_mem)
                return f"Updated {key} to {value}"
            return "Error: key and value required for update_nested"
        
        elif action_type == 'retrieve_data':
            # Retrieve specific data from memory or tasks
            data_type = args.get('data_type', 'memory')
            section = args.get('section')
            key = args.get('key')
            query = args.get('query')
            
            # Special case handling for common fields that might be requested without full path
            common_fields = {
                "name": "personal.name", 
                "full_name": "personal.full_name",
                "age": "personal.age",
                "height": "personal.height",
                "weight": "personal.weight",
                "birthday_preferences": "personal.birthday_preferences",
                "friends": "personal.friends"
            }
            
            if section in common_fields:
                section = common_fields[section]
            
            if data_type == 'memory':
                user_mem = memory_manager.get_user_memory()
                
                # Handle direct field access first (no section or with "personal." prefix)
                if section:
                    # If section contains dots, it's a nested path
                    if '.' in section:
                        parts = section.split('.')
                        curr = user_mem
                        for p in parts:
                            if p in curr:
                                curr = curr[p]
                            else:
                                return {
                                    "type": "error",
                                    "message": f"Path {section} not found in memory"
                                }
                        return {
                            "type": "memory_data",
                            "path": section,
                            "data": curr
                        }
                    # Otherwise check top-level sections first
                    elif section in user_mem:
                        if key and key in user_mem[section]:
                            return {
                                "type": "memory_data",
                                "section": section,
                                "key": key,
                                "data": user_mem[section][key]
                            }
                        else:
                            return {
                                "type": "memory_data",
                                "section": section,
                                "data": user_mem[section]
                            }
                    # Check if it's a direct field in personal section
                    elif section in user_mem.get('personal', {}):
                        return {
                            "type": "memory_data", 
                            "section": "personal",
                            "key": section,
                            "data": user_mem['personal'][section]
                        }
                    else:
                        # Try to find it anywhere in memory
                        for sect_name, sect_data in user_mem.items():
                            if isinstance(sect_data, dict) and section in sect_data:
                                return {
                                    "type": "memory_data",
                                    "section": sect_name,
                                    "key": section,
                                    "data": sect_data[section]
                                }
                        
                        return {
                            "type": "error",
                            "message": f"Section '{section}' not found in memory"
                        }
                
                # Search by query across all sections
                elif query:
                    results = {}
                    query_lower = query.lower()
                    
                    for section_name, section_data in user_mem.items():
                        if isinstance(section_data, dict):
                            for key_name, value in section_data.items():
                                if (query_lower in key_name.lower() or 
                                    (isinstance(value, str) and query_lower in value.lower())):
                                    if section_name not in results:
                                        results[section_name] = {}
                                    results[section_name][key_name] = value
                                        
                    return {
                        "type": "memory_data", 
                        "query": query,
                        "data": results
                    }
                # Return entire memory if no specific section/query
                else:
                    return {
                        "type": "memory_data",
                        "data": user_mem
                    }
                    
            elif data_type == 'tasks':
                # Handle tasks retrieval
                file_path = self._resolve_path(args.get('file', 'data-backend/tasks.md'))
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        tasks_content = f.read()
                    
                    # Filter by query if provided
                    if query:
                        filtered_lines = []
                        for line in tasks_content.split('\n'):
                            if query.lower() in line.lower():
                                filtered_lines.append(line)
                        return {
                            "type": "tasks_data",
                            "query": query,
                            "data": '\n'.join(filtered_lines)
                        }
                    else:
                        return {
                            "type": "tasks_data",
                            "data": tasks_content
                        }
                else:
                    return {
                        "type": "error",
                        "message": f"Task file {file_path} not found"
                    }
                    
            else:
                return {
                    "type": "error",
                    "message": f"Unknown data type: {data_type}"
                }
        else:
            return f"Unknown action: {action_type}"
    
    def _resolve_path(self, file_path):
        """Convert relative paths to absolute paths"""
        if not os.path.isabs(file_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_dir, file_path)
        return file_path
