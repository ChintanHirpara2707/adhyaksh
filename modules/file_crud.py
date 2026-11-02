"""
=============================================================================
ADHYAKSH AI // Full File & Directory CRUD Operations Engine
Create, Read/View, Update, Delete (Safe Recycle & Permanent), and Explore
=============================================================================
"""

import os
import datetime
import subprocess
from config import BASE_DIR, DEFAULT_WORK_DRIVE, AVAILABLE_DRIVES, get_available_drives

# Safe file deletion using Send2Trash if available
try:
    import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

def get_live_search_directories():
    """Dynamically builds list of system search paths including all active laptop drives."""
    roots = [
        BASE_DIR,
        DEFAULT_WORK_DRIVE,
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
    ]
    for d in get_available_drives():
        if d not in roots and os.path.exists(d):
            roots.append(d)
    return roots

SEARCH_DIRECTORIES = get_live_search_directories()

def resolve_target_directory(text: str) -> str:
    """Detects target laptop drive or folder from text, dynamically resolving connected drives."""
    text_lower = text.lower()
    live_drives = get_available_drives()
    
    # 1. Check drive letters from all live drives
    for drive in live_drives:
        letter = drive[0].lower()
        if f"{letter} drive" in text_lower or f"{letter}:" in text_lower or f"in {letter}" in text_lower or f"on {letter}" in text_lower or f"{letter} ma" in text_lower or f"{letter} me" in text_lower:
            return drive

    # 2. Check for standard folders
    if "desktop" in text_lower:
        return os.path.expanduser("~/Desktop")
    elif "documents" in text_lower:
        return os.path.expanduser("~/Documents")
    elif "downloads" in text_lower:
        return os.path.expanduser("~/Downloads")

    # 3. Default to available primary work drive or project base directory
    return DEFAULT_WORK_DRIVE if os.path.exists(DEFAULT_WORK_DRIVE) else (live_drives[0] if live_drives else BASE_DIR)


def find_file(filename_or_path: str) -> str | None:
    """Finds exact or relative path of a file across system search paths."""
    clean = filename_or_path.strip().strip("'\"")
    # 1. Exact existing path
    if os.path.isabs(clean) and os.path.exists(clean):
        return os.path.abspath(clean)

    # 2. Check directly in search roots
    for root_dir in SEARCH_DIRECTORIES:
        if os.path.exists(root_dir):
            candidate = os.path.join(root_dir, clean)
            if os.path.exists(candidate) and os.path.isfile(candidate):
                return os.path.abspath(candidate)

    # 3. Walk 2-levels deep in search roots
    for root_dir in SEARCH_DIRECTORIES[:4]:
        if os.path.exists(root_dir):
            try:
                for root, dirs, files in os.walk(root_dir):
                    # Depth limit
                    rel_depth = root[len(root_dir):].count(os.sep)
                    if rel_depth > 2:
                        continue
                    for f in files:
                        if f.lower() == clean.lower():
                            return os.path.abspath(os.path.join(root, f))
            except Exception:
                continue

    return None


# ---------------------------------------------------------------------------
# 1. CREATE FILE & DIRECTORY
# ---------------------------------------------------------------------------
def create_file(
    filename: str,
    target_directory: str = None,
    content: str = "",
    open_in_editor: bool = False
) -> tuple[bool, str, str]:
    """
    Creates a new physical file with optional content.
    Returns: (success, message, file_path)
    """
    clean_name = filename.strip(" :,'\"<>")
    if not clean_name:
        clean_name = "new_document.txt"
    if "." not in clean_name:
        clean_name += ".txt"

    dir_path = target_directory or DEFAULT_WORK_DRIVE
    if not os.path.exists(dir_path):
        dir_path = BASE_DIR

    file_path = os.path.join(dir_path, clean_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    default_content = content or f"# File: {clean_name}\n# Created by ADHYAKSH AI on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n# Autonomous Executive System\n\n"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(default_content)

        opened_in = ""
        if open_in_editor:
            import shutil
            try:
                if shutil.which("code"):
                    subprocess.Popen(f'code "{file_path}"', shell=True)
                    opened_in = " and opened in **Visual Studio Code**"
                else:
                    os.startfile(file_path)
                    opened_in = " and opened in default editor"
            except Exception:
                try:
                    os.startfile(file_path)
                    opened_in = " and opened in default editor"
                except Exception:
                    pass

        msg = f"**File Created Successfully:** `{file_path}`{opened_in}!\n- **Size:** `{len(default_content)} bytes`\n- **Timestamp:** `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}`"
        return True, msg, file_path

    except Exception as e:
        return False, f"Error creating file `{file_path}`: `{str(e)}`", ""


def create_directory(dirname: str, target_directory: str = None, open_in_explorer: bool = False) -> tuple[bool, str, str]:
    """Creates a new physical folder."""
    clean_name = dirname.strip(" :,'\"<>")
    if not clean_name:
        clean_name = "new_folder"

    dir_path = target_directory or DEFAULT_WORK_DRIVE
    if not os.path.exists(dir_path):
        dir_path = BASE_DIR

    full_path = os.path.join(dir_path, clean_name)
    try:
        os.makedirs(full_path, exist_ok=True)
        if open_in_explorer:
            subprocess.Popen(f'explorer "{full_path}"', shell=True)
            msg = f"**Folder Created Successfully:** `{full_path}` and opened in Windows Explorer!"
        else:
            msg = f"**Folder Created Successfully:** `{full_path}`"
        return True, msg, full_path
    except Exception as e:
        return False, f"Error creating folder `{full_path}`: `{str(e)}`", ""


# ---------------------------------------------------------------------------
# 2. READ / VIEW FILE
# ---------------------------------------------------------------------------
def read_file_content(filename_or_path: str, max_chars: int = 50000) -> tuple[bool, str, dict]:
    """
    Reads the content and metadata of a file.
    Returns: (success, content_or_error_message, metadata_dict)
    """
    filepath = find_file(filename_or_path)
    if not filepath:
        return False, f"File `{filename_or_path}` was not found in project or search drives.", {}

    try:
        size = os.path.getsize(filepath)
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d %H:%M:%S")

        # Check file extension for text vs binary
        ext = os.path.splitext(filepath)[1].lower()
        binary_exts = [".exe", ".dll", ".png", ".jpg", ".jpeg", ".zip", ".tar", ".bin", ".mp3", ".wav", ".mp4"]
        
        if ext in binary_exts:
            meta = {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "size_kb": round(size / 1024, 2),
                "last_modified": mod_time,
                "is_binary": True
            }
            return True, f"[Binary file: {os.path.basename(filepath)} ({round(size/1024, 2)} KB). Binary preview is suppressed.]", meta

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)

        truncated = len(content) == max_chars and size > max_chars
        line_count = content.count("\n") + 1

        meta = {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "size_kb": round(size / 1024, 2),
            "last_modified": mod_time,
            "line_count": line_count,
            "truncated": truncated,
            "extension": ext or ".txt"
        }
        return True, content, meta

    except Exception as e:
        return False, f"Error reading file `{filepath}`: `{str(e)}`", {}


# ---------------------------------------------------------------------------
# 3. UPDATE FILE
# ---------------------------------------------------------------------------
def update_file_content(
    filename_or_path: str,
    new_content: str,
    mode: str = "append"
) -> tuple[bool, str, dict]:
    """
    Updates an existing file by appending to it or completely replacing its contents.
    Mode: 'append' | 'overwrite'
    Returns: (success, message, metadata_dict)
    """
    filepath = find_file(filename_or_path)
    if not filepath:
        # If file doesn't exist, create it anew
        succ, msg, created_path = create_file(filename_or_path, content=new_content)
        return succ, f"File did not exist, so it was created: {msg}", {"filepath": created_path}

    try:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if mode == "append":
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"\n{new_content}")
            action_desc = "Appended new content to"
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            action_desc = "Overwrote content of"

        new_size = os.path.getsize(filepath)
        meta = {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "size_kb": round(new_size / 1024, 2),
            "updated_at": now_str,
            "mode": mode
        }
        msg = f"**File Updated Successfully:** {action_desc} `{filepath}`\n- **New Size:** `{round(new_size/1024, 2)} KB`\n- **Timestamp:** `{now_str}`"
        return True, msg, meta

    except Exception as e:
        return False, f"Error updating file `{filepath}`: `{str(e)}`", {}


# ---------------------------------------------------------------------------
# 4. DELETE FILE (SAFE RECYCLE & PERMANENT)
# ---------------------------------------------------------------------------
def delete_file_safely(filename_or_path: str, permanent: bool = False) -> tuple[bool, str]:
    """
    Deletes a file safely using Windows Recycle Bin (Send2Trash) or permanently if requested.
    Returns: (success, message)
    """
    filepath = find_file(filename_or_path)
    if not filepath:
        return False, f"Target file `{filename_or_path}` could not be found to delete."

    try:
        fname = os.path.basename(filepath)
        if permanent:
            os.remove(filepath)
            return True, f"**File Deleted Permanently:** `{filepath}` has been removed from the system."
        else:
            if HAS_SEND2TRASH:
                send2trash.send2trash(filepath)
                return True, f"**File Moved to Recycle Bin:** `{fname}` was safely sent to Windows Recycle Bin. It can be restored if needed."
            else:
                os.remove(filepath)
                return True, f"**File Deleted:** `{fname}` was removed from `{filepath}`."
    except Exception as e:
        return False, f"Error deleting file `{filepath}`: `{str(e)}`"


# ---------------------------------------------------------------------------
# 5. DIRECTORY LISTING & EXPLORATION
# ---------------------------------------------------------------------------
def list_directory_contents(directory_path: str) -> list[dict]:
    """Lists files and subdirectories with sizes, modified times, and types."""
    target = os.path.abspath(directory_path) if os.path.exists(directory_path) else BASE_DIR
    items = []
    try:
        with os.scandir(target) as it:
            for entry in it:
                try:
                    stat = entry.stat()
                    is_dir = entry.is_dir()
                    size_kb = round(stat.st_size / 1024, 2) if not is_dir else 0
                    mod_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    items.append({
                        "name": entry.name,
                        "path": entry.path,
                        "is_dir": is_dir,
                        "type": "Folder" if is_dir else (os.path.splitext(entry.name)[1].upper() or "File"),
                        "size_kb": size_kb,
                        "modified": mod_time
                    })
                except Exception:
                    continue
        # Sort folders first, then alphabetically
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    except Exception as e:
        print(f"Error reading directory {target}: {e}")
    return items
