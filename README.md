# Chinese Daily Planner

This is a simple web application built with Python and the FastHTML framework to act as a daily planner and notes app, initially focused on language learning tasks.

## Features

*   Monthly calendar view.
*   Clickable dates to view/edit daily notes.
*   Predefined daily task templates (editable).
*   Markdown support for notes using EasyMDE (with live preview).
*   Interactive checkboxes for tasks within daily notes.
*   Minimalist, themeable interface.

## Prerequisites

*   Python 3.8+ (or newer)
*   `pip` (Python package installer)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd chinese-daily
    ```

2.  **Create and activate a virtual environment:**
    *   **Windows (Command Prompt/PowerShell):**
        ```powershell
        python -m venv .venv
        .venv\Scripts\activate
        ```
    *   **macOS/Linux (Bash/Zsh):**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Make sure your virtual environment is activated (`.venv\Scripts\activate` or `source .venv/bin/activate`).
2.  Run the Uvicorn server from the project root directory:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dirs app
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:8000` or `http://localhost:8000`.

## Project Structure

The core application logic resides within the `app/` directory:

*   `main.py`: Main application entry point, FastAPI app initialization, static file mounting, route module imports.
*   `config.py`: Stores configuration constants like directory paths, days of the week, UI settings.
*   `services/`: Contains non-web-specific business logic:
    *   `storage.py`: Handles all file reading and writing operations (tasks, notes).
    *   `markdown.py`: Configures and uses the Mistune markdown parser.
    *   `calendar.py`: Contains calendar generation logic.
*   `ui/`: Contains reusable UI component generation functions:
    *   `components.py`: Helpers for sidebar, navigation buttons, etc.
*   `web/`: Contains the web route handlers (controllers), separated by functionality:
    *   `routes_calendar.py`: Handles the root ('/') path and calendar display.
    *   `routes_tasks.py`: Handles editing/saving task templates and toggling task checkboxes.
    *   `routes_notes.py`: Handles displaying/saving daily notes.
*   `static/`: Contains static assets like `style.css`.

## Data Storage

*   **Task Templates:** Markdown files stored in the `tasks/` directory (e.g., `tasks/monday.md`).
*   **Daily Notes & Task State:** Combined markdown files stored in the `data/` directory, named by date (e.g., `data/2023-10-27_notes.md`). Checkbox states are saved directly within the task list in these files. 
