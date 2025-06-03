import os
from .utils import read_file, write_file

DEFAULT_TASKS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data-backend', 'tasks.md')

class Editor:
    def __init__(self):
        pass

    def apply_edit(self, file_path, new_content):
        # Ensure directory exists before writing file
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        write_file(file_path, new_content)

    def read_markdown(self, file_path):
        return read_file(file_path)
    
    def append_to_markdown(self, file_path, content):
        """Append content to a markdown file"""
        current_content = read_file(file_path)
        if current_content:
            new_content = current_content + "\n" + content
        else:
            new_content = content
        write_file(file_path, new_content)
        
    def add_task(self, file_path=None, task=None):
        """Add a task to the tasks file"""
        if file_path is None:
            file_path = DEFAULT_TASKS_FILE
        tasks = self.read_markdown(file_path)
        if not tasks.strip():
            tasks = "# Tasks\n\n"
        # Add the task if it doesn't already exist
        if f"- [ ] {task}" not in tasks:
            if not tasks.endswith("\n\n"):
                if tasks.endswith("\n"):
                    tasks += "\n"
                else:
                    tasks += "\n\n"
            tasks += f"- [ ] {task}\n"
            write_file(file_path, tasks)
            
    def complete_task(self, file_path=None, task=None):
        """Mark a task as completed"""
        if file_path is None:
            file_path = DEFAULT_TASKS_FILE
        tasks = self.read_markdown(file_path)
        if f"- [ ] {task}" in tasks:
            tasks = tasks.replace(f"- [ ] {task}", f"- [x] {task}")
            write_file(file_path, tasks)
            return True
        return False

    def add_cron_job(self, file_path, schedule, task):
        """Add a scheduled job to the cron file"""
        cron = self.read_markdown(file_path)
        if not cron.strip():
            cron = "# Cron: Scheduled Routines\n\n"
        # Add the cron job if it doesn't already exist
        new_job = f"- {schedule}: {task}"
        if new_job not in cron:
            if not cron.endswith("\n\n"):
                if cron.endswith("\n"):
                    cron += "\n"
                else:
                    cron += "\n\n"
            cron += f"{new_job}\n"
            write_file(file_path, cron)

    def update_section(self, file_path, section_title, new_section_content):
        content = read_file(file_path)
        lines = content.split('\n')
        new_lines = []
        in_section = False
        for line in lines:
            if line.strip().startswith(f'# {section_title}'):
                in_section = True
                new_lines.append(line)
                new_lines.append(new_section_content)
                continue
            if in_section and line.strip().startswith('#') and not line.strip().startswith(f'# {section_title}'):
                in_section = False
            if not in_section:
                new_lines.append(line)
        write_file(file_path, '\n'.join(new_lines))
