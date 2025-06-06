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
            except Exception:
                pass
        
        return {
            "description": description,
            "status": status,
            "priority": priority,
            "age": age,
            "subtasks": task_data.get("subtasks", []),
            "dependencies": task_data.get("dependencies", []),
            "id": task_data.get("id", "")
        }
    return None
