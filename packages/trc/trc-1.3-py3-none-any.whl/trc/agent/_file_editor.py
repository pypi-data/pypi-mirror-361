# agent/file_editor.py
# -- Import packages --
import os
from .._filetools import _os_to_dict as os_to_dict

# -- File Editor Prompt --
_FILE_EDITOR_PROMPT = """
**File Editor**: Read, write, append, and list files from your workspace.
    * **Read**: `<<<FILE:'read'<nex!-pr-amtre?gr+>'path/to/file.txt'>>>`
    * **Write**: `<<<FILE:'write'<nex!-pr-amtre?gr+>'path/to/file.txt'<nex!-pr-amtre?gr+>'content_to_write'>>>` (overwrites file)
    * **Append**: `<<<FILE:'append'<nex!-pr-amtre?gr+>'path/to/file.txt'<nex!-pr-amtre?gr+>'content_to_append'>>>`
    * **List**: `<<<FILE:'list'<nex!-pr-amtre?gr+>'path/to/directory'<nex!-pr-amtre?gr+>'recursive'<nex!-pr-amtre?gr+>'size'<nex!-pr-amtre?gr+>'type'<nex!-pr-amtre?gr+>'content'>>>`. Use this to retrieve structured info from a file or directory. Set recursive (bool) to true to list directories recursively. Set size, type, and content (bool) to true to include size in bytes, file type (file/directory + extension), and file content. Content returns only the first 50 charakters of the file.
    * **Example**: `<<<FILE:'read'<nex!-pr-amtre?gr+>'data.txt'>>>`, `<<<FILE:'write'<nex!-pr-amtre?gr+>'data.txt'<nex!-pr-amtre?gr+>'Hello World!'>>>`, `<<<FILE:'list'<nex!-pr-amtre?gr+>'.'<nex!-pr-amtre?gr+>'ls'<nex!-pr-amtre?gr+>'[True, False, True, 100]'>>>`.
    * **IMPORTANT**: Never use a backslash for a quote or before a quote if not needed for something special.
    * **Info**: if you want to write a literal backslash (`\`) to a file(so that the backslash is like any other character), use <bs> instead. Don't use this for newlines. NEVER!! Use `\n` for newlines. This counts for every newsline in every file_format.
"""

# -- File Editor Class --
class _FileEditor:
    def __init__(self, config: dict):
        self.agent_base_dir = config["agent_base_dir"]
    # Helper Function
    def _get_agent_path(self, file_path: str=".") -> str:
        # Prevent directory traversal attacks
        sanitized_path = os.path.normpath(file_path).lstrip('./\\')
        return os.path.join(self.agent_base_dir, sanitized_path)

    # Read Tool
    def read(self, file_path: str=".") -> str:
        try:
            full_path = self._get_agent_path(file_path)
            with open(full_path, 'r', encoding='utf-8') as file:
                return f"Content of file at {file_path} is:\n{file.read()}"

        except FileNotFoundError:
            return f"Error: File not found at '{file_path}'."

        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

    # Write Tool
    def write(self, file_path: str=".", content: str="") -> str:
        try:
            content = content.replace("\\'", "'")
            content = content.replace('\\"', '"')
            content = content.replace("\\n", "\n")
            content = content.replace("\\t", "\t")
            content = content.replace("<bs>", "\\")
            full_path = self._get_agent_path(file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return f"Successfully wrote to '{file_path}'."

        except Exception as e:
            return f"Error writing to file '{file_path}': {e}"

    # Append Tool
    def append(self, file_path: str=".", content: str="") -> str:
        try:
            content = content.replace("\'", "'")
            content = content.replace('\"', '"')
            content = content.replace("\\n", "\n")
            content = content.replace("\\t", "\t")
            content = content.replace("<bs>", "\\")
            full_path = self._get_agent_path(file_path)
            with open(full_path, 'a', encoding='utf-8') as file:
                file.write(content)
            return f"Successfully appended to '{file_path}'."

        except Exception as e:
            return f"Error appending to file '{file_path}': {e}"

    # List Tool
    def lister(self, directory_path: str=".", recursive: bool=False, size: bool=False, type: bool=False, content: bool=False) -> str:
        recursive = bool(recursive)
        size = bool(size)
        type = bool(type)
        content = bool(content)
        try:
            full_path = self._get_agent_path(directory_path)
            dicti = os_to_dict(full_path, recursive, size, type, content, 50)
            if directory_path == "." or directory_path == "" or directory_path == "/":
                if dicti['listed_path'].split("/")[0] == self.agent_base_dir:
                    dicti['listed_path'] = directory_path
            return f"Listed directory: {dict(dicti)}"
        except Exception as e:
            return f"Error listing directory '{directory_path}': {e}"