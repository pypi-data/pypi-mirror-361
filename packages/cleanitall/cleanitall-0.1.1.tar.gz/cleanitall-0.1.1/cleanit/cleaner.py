import os
import shutil

JUNK_EXTENSIONS = ['.pyc', '.pyo', '.log', '.tmp', '.bak']
JUNK_FOLDERS = ['__pycache__', '.ipynb_checkpoints']
JUNK_FILES = ['.DS_Store', 'Thumbs.db']

def get_junk_files(path: str):
    junk = []
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if d in JUNK_FOLDERS:
                junk.append(os.path.join(root, d))
        for f in files:
            if f in JUNK_FILES or os.path.splitext(f)[1] in JUNK_EXTENSIONS:
                junk.append(os.path.join(root, f))
    return junk

def delete_junk(junk_files: list[str]) -> int:
    total_deleted_size = 0
    for item in junk_files:
        if os.path.isdir(item):
            total_deleted_size += get_size(item)
            shutil.rmtree(item, ignore_errors=True)
        else:
            total_deleted_size += os.path.getsize(item)
            os.remove(item)
    return total_deleted_size

def get_size(path: str) -> int:
    if os.path.isfile(path):
        return os.path.getsize(path)
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except:
                pass
    return total
