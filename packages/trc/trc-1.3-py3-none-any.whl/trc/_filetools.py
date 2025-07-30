# filetools.py
# -- Import packages --
import json, shutil, os

# -- Load a JSON file into a dictionary --
def _json_to_dict(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Error loading JSON file: {e}")

# -- Save a dictionary to a JSON file --
def _dict_to_json(path: str, data: dict):
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise Exception(f"Error saving JSON file: {e}")

# -- Copy a file --
def _copy_file(src: str, dst: str, overwrite: bool=False):
    try:
        if os.path.exists(dst) and not overwrite:
            raise Exception("Destination file exists and overwrite is False")
        shutil.copy2(src, dst)
    except Exception as e:
        raise Exception(f"Error copying file: {e}")

# -  Get metadata of a file or directory --
def _get_metadata(path: str) -> dict:
    if not os.path.exists(path):
        return {"error": f"Path not found: {path}"}

    metadata = {}
    if os.path.isfile(path):
        metadata["type"] = "file"
        metadata["extension"] = os.path.splitext(path)[1]
        metadata["size"] = os.path.getsize(path)
    elif os.path.isdir(path):
        metadata["type"] = "directory"
        metadata["extension"] = ""
        total_size = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        metadata["size"] = total_size
    else:
        metadata["type"] = "unknown"
        metadata["extension"] = ""
        metadata["size"] = 0

    return metadata

# -- List the contents of a directory --
def _os_to_dict(
    path: str,
    recursive: bool = False,
    size: bool = False,
    type: bool = False,
    content: bool = False,
    maxlen: int = 0
) -> dict:
    result = {
        "listed_path": path,
        "content": {}
    }

    if not os.path.exists(path):
        return {"error": f"Path not found: {path}"}

    def read_file_content(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
                if maxlen > 0 and len(data) > maxlen:
                    return data[:maxlen] + "..."
                return data
        except Exception:
            return "Non readable content"

    # Process a single file or directory
    def process_entry(entry_path: str) -> dict:
        entry_data = {}
        if type:
            entry_data["type"] = "file" if os.path.isfile(entry_path) else "directory"
            if os.path.isfile(entry_path):
                entry_data["extension"] = os.path.splitext(entry_path)[1]
        if size:
            entry_data["size"] = os.path.getsize(entry_path) if os.path.isfile(entry_path) else _get_metadata(entry_path)["size"]
        if content and os.path.isfile(entry_path):
            entry_data["content"] = read_file_content(entry_path)
        return entry_data

    # Process a directory
    def process_directory(current_path: str) -> dict:
        structure = {}
        try:
            entries = sorted(os.listdir(current_path))
            for entry in entries:
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path) and recursive:
                    structure[entry] = process_entry(full_path)
                    structure[entry]["content"] = process_directory(full_path)
                else:
                    structure[entry] = process_entry(full_path)
        except Exception as e:
            structure["error"] = f"Could not access directory '{current_path}': {e}"
        return structure

    if os.path.isfile(path):
        result["content"] = process_entry(path)
    elif os.path.isdir(path):
        result["content"] = process_directory(path)
    else:
        result["error"] = "Unsupported path type."

    return result