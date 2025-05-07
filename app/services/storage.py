# Using . for relative import from sibling module
from .. import config 
import os # Keep os for join, though Path objects handle slashes

# --- Task Template Files --- #

def read_tasks_template(day_name: str) -> str | None:
    """Reads the task template markdown for a given day name."""
    p = config.TASKS_DIR / f"{day_name.lower()}.md"
    try:
        return p.read_text(encoding="utf-8") if p.exists() else None
    except OSError as e:
        print(f"Error reading task template {p}: {e}")
        return None

def write_tasks_template(day_name: str, content: str) -> bool:
    """Writes content to the task template file for a given day name. Returns True on success."""
    p = config.TASKS_DIR / f"{day_name.lower()}.md"
    try:
        # Ensure directory exists
        config.TASKS_DIR.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return True
    except OSError as e:
        print(f"Error writing task template {p}: {e}")
        return False

# --- Daily Notes/Data Files --- #

def read_notes_file(date_str: str) -> str | None:
    """Reads the full content of the notes file for a given date string (YYYY-MM-DD)."""
    p = config.DATA_DIR / f"{date_str}_notes.md"
    try:
        return p.read_text(encoding="utf-8") if p.exists() else None
    except OSError as e:
        print(f"Error reading notes file {p}: {e}")
        return None

def write_notes_file(date_str: str, content: str) -> bool:
    """Writes content to the notes file for a given date string (YYYY-MM-DD). Returns True on success."""
    p = config.DATA_DIR / f"{date_str}_notes.md"
    try:
        # Ensure directory exists
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return True
    except OSError as e:
        print(f"Error writing notes file {p}: {e}")
        return False

def read_notes_for_editing(date_str: str) -> str:
    """Reads the notes file and extracts only the part after the separator for editing."""
    full_content = read_notes_file(date_str)
    if full_content is None:
        return "" # Return empty string if file doesn't exist
    
    parts = full_content.split(config.NOTES_SEPARATOR, 1)
    if len(parts) == 2:
        return parts[1] # Return content after separator
    else:
        # Separator not found, assume entire content is notes (legacy or notes-only)
        return full_content

def read_tasks_for_display(date_str: str, day_name: str) -> str:
    """Gets the task markdown, prioritizing the saved notes file, falling back to template."""
    full_content = read_notes_file(date_str)
    tasks_markdown = None
    
    if full_content is not None:
        parts = full_content.split(config.NOTES_SEPARATOR, 1)
        if len(parts) == 2:
            tasks_markdown = parts[0]
        else:
             tasks_markdown = read_tasks_template(day_name)
    else:
        tasks_markdown = read_tasks_template(day_name)

    if tasks_markdown is None:
        # If template also didn't exist or failed reading
        return f"## Tasks for {day_name.capitalize()}\n\n_(No tasks defined)_"
    return tasks_markdown

def read_raw_tasks(date_str: str, day_name: str) -> str:
    """Reads the raw task markdown for a given date, prioritizing daily file, then template, then empty."""
    daily_file_content = read_notes_file(date_str)

    if daily_file_content is not None:
        parts = daily_file_content.split(config.NOTES_SEPARATOR, 1)
        if len(parts) == 2:
            return parts[0].strip()  # Return task part from daily file
        # If daily file exists but no separator, fall through to template logic
        # (assuming it might be all notes or malformed for task/notes structure)

    # Try to load from template if daily file had no tasks or didn't exist
    template_content = read_tasks_template(day_name)
    if template_content is not None:
        return template_content.strip()

    # Default to empty string if no tasks found in daily file or template
    return ""

def save_full_notes_content(date_str: str, day_name: str, notes_content: str) -> bool:
    """Constructs the full notes file content (tasks + separator + notes) and saves it."""

    # do not read_tasks_template here, we want to read the specific tasks for the date
    tasks_markdown = read_tasks_for_display(date_str, day_name)
    print(f"tasks_markdown: {tasks_markdown}")
    if tasks_markdown is None:
        print(f"Warning: Task template for {day_name} not found when saving notes for {date_str}. Saving notes without tasks.")
        tasks_markdown = f"## Tasks for {day_name.capitalize()}\n\n_(Template not found at time of save)_" # Or maybe just empty string?

    final_content = f"{tasks_markdown.strip()}{config.NOTES_SEPARATOR}{notes_content}"
    return write_notes_file(date_str, final_content)

def save_raw_tasks(date_str: str, day_name: str, new_tasks_markdown: str) -> bool:
    """Saves new task markdown, preserving existing notes if any."""
    existing_full_content = read_notes_file(date_str)
    existing_notes_part = "" # Default to empty notes

    if existing_full_content is not None:
        parts = existing_full_content.split(config.NOTES_SEPARATOR, 1)
        if len(parts) == 2:
            # Separator found, preserve notes part
            existing_notes_part = parts[1]
        else:
            # No separator found in existing file, assume all existing content is notes
            existing_notes_part = existing_full_content
    else:
        # File doesn't exist. Notes part will be empty. 
        # We might want to ensure new_tasks_markdown isn't None or empty here
        # or that behavior is handled by the caller or desired.
        pass # existing_notes_part remains ""

    # Construct the new full content
    # .strip() on new_tasks_markdown to remove any leading/trailing whitespace from editor
    final_content = f"{new_tasks_markdown.strip()}{config.NOTES_SEPARATOR}{existing_notes_part}"
    
    # Ensure DATA_DIR exists (write_notes_file also does this, but can be good practice)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return write_notes_file(date_str, final_content)

def toggle_task_in_notes(date_str: str, task_index: int) -> bool:
    """Toggles the state of a task checkbox within the notes file."""
    notes_content = read_notes_file(date_str)
    if notes_content is None:
        print(f"Error toggle_task: Cannot toggle task, notes file not found: {date_str}")
        return False

    lines = notes_content.splitlines(keepends=True) # Keep newlines for writing
    task_lines_indices = [] # Store tuples of (line_index_in_file, line_content)
    in_task_section = False
    separator_line_index = -1

    # First pass: Identify task lines and the separator
    for i, line in enumerate(lines):
        line_strip = line.strip()

        # Check for separator first to define the end boundary
        if config.NOTES_SEPARATOR.strip() in line_strip:
            separator_line_index = i
            break # Stop scanning for tasks once separator is found

        # Determine if we are in the task section
        # Assume task section starts from line 0 unless a specific header is found
        # Note: This assumes tasks appear BEFORE the separator.
        # A simple heuristic: if we haven't found the separator yet, we are potentially in the task section.
        # We will filter actual task *items* below.
        # If a header like "## Tasks" exists, we could use it as a firmer start, but 
        # let's keep it simple and just check lines before the separator.

        # Identify actual task list items
        stripped_line_l = line.lstrip()
        is_task_line = stripped_line_l.startswith("- [ ]") or stripped_line_l.startswith("- [x]")
        
        if is_task_line:
            # We only care about task lines before the separator (if found)
            if separator_line_index == -1: 
                task_lines_indices.append(i) # Store the original line index
            # If separator_line_index is set, we've already passed the task section
            
    # Second pass: Check index and modify
    found_and_modified = False
    if 0 <= task_index < len(task_lines_indices):
        line_to_modify_index = task_lines_indices[task_index]
        original_line = lines[line_to_modify_index]
        modified_line = None

        if "- [ ]" in original_line:
            modified_line = original_line.replace("- [ ]", "- [x]", 1)
        elif "- [x]" in original_line:
            modified_line = original_line.replace("- [x]", "- [ ]", 1)

        if modified_line is not None and modified_line != original_line:
            lines[line_to_modify_index] = modified_line
            found_and_modified = True
            print(f"--- Storage: Successfully toggled task index {task_index} on line {line_to_modify_index} for {date_str}. ---")
        else:
            print(f"--- WARNING Storage: Task index {task_index} line {line_to_modify_index} content '{original_line.strip()}' did not contain expected pattern or replace failed for {date_str}. ---")

    else:
        print(f"Error Storage: Task index {task_index} is out of bounds for {date_str}. Found {len(task_lines_indices)} task lines.")

    if not found_and_modified:
        # Error message printed above
        return False

    # Join lines back and write
    success = write_notes_file(date_str, "".join(lines))
    if success:
        print(f"--- Storage: Successfully saved notes file for {date_str} after task toggle.")
    else:
        print(f"--- Storage Error: Failed to write notes file for {date_str} after task toggle.")
    return success 