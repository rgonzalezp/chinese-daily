# UI Component Definitions Index

This file lists key Python functions that generate reusable HTML UI components or blocks within the application.

## General UI Components

*   **Component:** Sidebar Navigation
    *   **Function:** `_generate_sidebar()`
    *   **Location:** `app/ui/components.py`
    *   **Description:** Generates the HTML for the main sidebar, including navigation links for editing task templates and other potential global actions.

*   **Component:** Day Navigation Button (for daily view)
    *   **Function:** `day_nav_button(text: str, target_date_str: str)`
    *   **Location:** `app/ui/components.py`
    *   **Description:** Creates a button used for navigating between days (Yesterday, Tomorrow, Last Week, Next Week) in the day detail view.

## Calendar Components

*   **Component:** Full Calendar View
    *   **Function:** `generate_calendar(year: int, month: int)`
    *   **Location:** `app/web/routes_calendar.py` (primarily, though it constructs HTML directly)
    *   **Description:** Generates the complete HTML for the monthly calendar grid and its controls.

## Daily View Components (`app/web/routes_notes.py`)

*   **Component:** Daily Navigation Bar
    *   **Function:** `_build_day_navigation(date_obj: datetime.date)`
    *   **Location:** `app/web/routes_notes.py`
    *   **Description:** Creates the top navigation bar for the day detail view, including "Back to Calendar" and day-to-day/week-to-week navigation buttons.

*   **Component:** Read-Only Tasks Block (Daily View)
    *   **Function:** `ReadOnlyTasksBlock(date_obj: datetime.date, date_str: str, day_name: str)`
    *   **Location:** `app/web/routes_notes.py`
    *   **Description:** Generates the display for tasks for a specific day, including task checkboxes. Double-clicking this block triggers the task editor. Integrates HTMX for task toggling.

*   **Component:** Tasks Editor Form (Daily View)
    *   **Function:** `TasksEditorForm(date_obj: datetime.date, date_str: str, day_name: str, raw_tasks_md: str, is_editable: bool)`
    *   **Location:** `app/web/routes_notes.py`
    *   **Description:** Generates the EasyMDE-based form for editing tasks for a specific day.

*   **Component:** Read-Only Notes View (Daily View)
    *   **Function:** `ReadOnlyNotesView(date_str: str, rendered_html: str)`
    *   **Location:** `app/web/routes_notes.py`
    *   **Description:** Displays rendered Markdown notes for a specific day. Double-clicking triggers the notes editor.

*   **Component:** Notes Editor Form (Daily View)
    *   **Function:** `NotesEditorForm(date_str: str, notes_content: str, is_editable: bool)`
    *   **Location:** `app/web/routes_notes.py`
    *   **Description:** Generates the EasyMDE-based form for editing notes for a specific day.

*   **Component:** Combined Day Detail Page Structure
    *   **Function:** `get_date_details_view(request: Request, date_str: str)`
    *   **Location:** `app/web/routes_notes.py`
    *   **Description:** While a route handler, this function orchestrates the assembly of the navigation, tasks block, and notes block for the full daily view page or HTMX fragment.

## Task Template Editor Components (`app/web/routes_tasks.py`)

*   **Component:** Task Template Editor View
    *   **Function:** `edit_tasks_view(request: Request, day_name: str)`
    *   **Location:** `app/web/routes_tasks.py`
    *   **Description:** Generates the page/form for editing the task template for a specific day of the week.

*(Note: This index focuses on functions primarily responsible for generating distinct UI blocks. Some route handlers also construct significant page structures.)* 