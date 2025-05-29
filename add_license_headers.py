"""
Script to add GPL V3 license headers to all Python files under src/.

Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import re

# Define the license header
LICENSE_HEADER = '''"""
Copyright (C) 2025 Roland Spatzenegger

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

'''

# Define the source directory
SRC_DIR = 'src'

# Files that have already been processed
PROCESSED_FILES = [
    os.path.join(SRC_DIR, 'config.py'),
    os.path.join(SRC_DIR, 'doc', '__main__.py')
]

def add_license_to_file(file_path):
    """Add the license header to a Python file if it doesn't already have it."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file already has a license header
    if 'Copyright (C) 2025 Roland Spatzenegger' in content:
        print(f"License already exists in {file_path}")
        return
    
    # If the file starts with a docstring, insert the license before the docstring content
    docstring_pattern = re.compile(r'^"""(.*?)"""', re.DOTALL)
    match = docstring_pattern.search(content)
    
    if match:
        # File has a docstring, insert license into it
        docstring_content = match.group(1).strip()
        new_docstring = f'"""\nCopyright (C) 2025 Roland Spatzenegger\n\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/>.\n\n{docstring_content}\n"""'
        new_content = docstring_pattern.sub(new_docstring, content, count=1)
    else:
        # File doesn't have a docstring, add license at the beginning
        new_content = LICENSE_HEADER + content
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added license to {file_path}")

def process_directory(directory):
    """Process all Python files in a directory and its subdirectories."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if file_path not in PROCESSED_FILES:
                    add_license_to_file(file_path)

if __name__ == "__main__":
    process_directory(SRC_DIR)
    print("License headers added to all Python files under src/")