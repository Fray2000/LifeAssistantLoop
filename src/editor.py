import os
from .utils import read_file, write_file

class Editor:
    def __init__(self):
        pass

    def apply_edit(self, file_path, new_content):
        write_file(file_path, new_content)

    def read_markdown(self, file_path):
        return read_file(file_path)

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
