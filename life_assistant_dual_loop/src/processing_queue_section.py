# Display processing queue section with dependencies
if task_tree["processing_queue"]:
    print(f"{Colors.BOLD}⏳ PROCESSING QUEUE ({len(task_tree['processing_queue'])} tasks){Colors.ENDC}")
    for i, task in enumerate(task_tree["processing_queue"]):
        is_last = i == len(task_tree["processing_queue"]) - 1
        prefix = self.icons['last_branch'] if is_last else self.icons['branch']
        
        priority_color = self._get_priority_color(task["priority"])
        priority_icon = self._get_priority_icon(task["priority"])
        status_icon = self._get_status_icon(task["status"])
        status_color = self._get_status_color(task["status"])
        
        age_info = f" ({task['age']})" if task["age"] else ""
        
        print(f"{priority_color}{prefix}{priority_icon}{status_color}{status_icon}{task['description']}{age_info}{Colors.ENDC}")
        
        # Display subtasks if any
        if task["subtasks"]:
            subtask_prefix = self.icons['empty'] if is_last else self.icons['continuation']
            self._display_subtasks(task["subtasks"], subtask_prefix)
        
        # Display dependencies if any
        if "dependencies" in task and task["dependencies"]:
            dep_prefix = self.icons['empty'] if is_last else self.icons['continuation']
            self._display_dependencies(task["dependencies"], dep_prefix)
    
    print()
