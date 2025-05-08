# Route Index

This file maps API routes to their corresponding handler functions in the codebase.

## Main Application Routes

*   **Route:** `/`
    *   **Handler:** `app.get("/")(get_calendar_view)` in `app/web/routes_calendar.py`
    *   **Description:** Displays the main calendar view for the current month. Also serves as the target for "Back to Calendar" buttons.

*   **Route:** `/calendar/{year}/{month}`
    *   **Handler:** `app.get("/calendar/{year}/{month}")(get_calendar_view)` in `app/web/routes_calendar.py`
    *   **Description:** Displays the calendar for a specific year and month.

## Daily View and Notes Routes

*   **Route:** `/view-day/{date_str}`
    *   **Handler:** `app.get("/view-day/{date_str}")(get_date_details_view)` in `app/web/routes_notes.py`
    *   **Description:** Displays the detailed view for a specific date, including tasks and notes.

*   **Route:** `/edit-notes/{date_str}` (GET)
    *   **Handler:** `app.get("/edit-notes/{date_str}")(get_notes_editor_component)` in `app/web/routes_notes.py`
    *   **Description:** Returns the EasyMDE editor form for editing notes for a specific date. Triggered by double-clicking the notes area.

*   **Route:** `/save-date/{date_str}` (POST)
    *   **Handler:** `app.post("/save-date/{date_str}")(save_date_notes)` in `app/web/routes_notes.py`
    *   **Description:** Saves the notes content for a specific date. Returns a feedback message.

## Daily Task Editing Routes (Specific Day)

*   **Route:** `/edit-day-tasks/{date_str}` (GET)
    *   **Handler:** `app.get("/edit-day-tasks/{date_str}")(get_tasks_editor_component)` in `app/web/routes_notes.py`
    *   **Description:** Returns the EasyMDE editor form for editing tasks for a specific date. Triggered by double-clicking the tasks area.

*   **Route:** `/save-day-tasks/{date_str}` (POST)
    *   **Handler:** `app.post("/save-day-tasks/{date_str}")(save_tasks_content)` in `app/web/routes_notes.py`
    *   **Description:** Saves the tasks content for a specific date. Returns the updated read-only task block.

*   **Route:** `/toggle-task/{date_str}/{idx}` (POST)
    *   **Handler:** `app.post("/toggle-task/{date_str}/{idx}")(toggle_task)` in `app/web/routes_notes.py` (previously in `routes_tasks.py`)
    *   **Description:** Toggles the completion state of a specific task item in the daily file.

## Task Template Editing Routes (Day of Week)

*   **Route:** `/edit-tasks/{day_name}` (GET)
    *   **Handler:** `app.get("/edit-tasks/{day_name}")(edit_tasks_view)` in `app/web/routes_tasks.py`
    *   **Description:** Displays an editor for the task template associated with a specific day of the week (e.g., "monday").

*   **Route:** `/save-tasks/{day_name}` (POST)
    *   **Handler:** `app.post("/save-tasks/{day_name}")(save_tasks_action)` in `app/web/routes_tasks.py`
    *   **Description:** Saves the content for a task template for a specific day of the week. Returns to the main calendar view with feedback. 