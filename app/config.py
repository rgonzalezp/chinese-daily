from pathlib import Path

# --- Directory Paths --- #
# Assume config.py is inside an 'app' directory, so parent is the project root
BASE_DIR = Path(__file__).resolve().parent.parent 
TASKS_DIR  = BASE_DIR / "tasks"
DATA_DIR   = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static" 

# --- Date/Time Constants --- #
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHORT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# --- HTMX/UI Constants --- #
CONTENT_SWAP_ID = "#content-swap-wrapper"
MAIN_CONTENT_ID = "#main-content-area"
SWAP_DELAY_MS = 322
NOTES_SEPARATOR = "\n---\n\n## My Notes\n\n" 