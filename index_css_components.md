# UI Component CSS Index

This file helps locate the CSS files responsible for styling different UI components.

## Components

*   **General Layout (`.layout-container`, `.sidebar`, `.main-content`)**: `static/css/layout.css`
*   **Theme Variables (`--primary-color`, etc.)**: `static/css/theme.css`
*   **Animations (General & FLIP for MDE fullscreen)**: `static/css/animations.css`
*   **Sidebar (`.sidebar-title`, `.sidebar-nav`, `.sidebar-button`)**: `static/css/sidebar.css`
*   **Sidebar Today Button (`.sidebar-today-button`)**: `static/css/sidebar.css`
*   **Calendar Controls (`.calendar-controls`, `.cal-nav`)**: `static/css/calendar.css`
*   **Calendar Grid (`.calendar-grid`, `.calendar-cell`)**: `static/css/calendar.css`
*   **Day Navigation (`.day-nav-container`, `.day-nav-button`)**: `static/css/day_nav.css`
*   **Weekday Navigation**: `static/css/weekday_nav.css`
*   **Markdown Content Styling (`.markdown-content`)**: `static/css/markdown.css`
*   **Notes Area (General)**: `static/css/notes.css`
*   **EasyMDE Editor (`.EasyMDEContainer`, `.editor-toolbar`)**: `static/css/easymde.css`
*   **Tasks List/Items (General Display)**: `static/css/tasks.css`
*   **Tasks Read-Only Block (`.tasks-readonly-block`)**: `static/css/tasks.css` (general task styling), `static/css/main.css` (for transitions)
*   **Tasks Editor Form (`.tasks-editor-form`)**: `static/css/tasks.css` (general task styling), `static/css/main.css` (for transitions)
*   **Task Block FLIP Animation (`.task-block-animate-transform`)**: `static/css/main.css`
*   **Task Template Editor Buttons (`.task-button-container`, save/cancel buttons in `routes_tasks.py`)**: 
    *   HTML: `app/web/routes_tasks.py` (in `edit_tasks_view`)
    *   CSS: `static/css/tasks.css` (likely, or general button styles)
*   **Feedback Section (`.feedback-msg`, `.success-msg`, `.error-msg`)**: `static/css/feedback.css`

*(Note: This index is based on current understanding and may need updates as the project evolves.)* 