import datetime
import uuid
import os

from starlette.requests import Request

# Assuming this file is in app/web/, import app from app/main.py
# --- Make imports relative to app package --- #
from ..main import app
from .. import config
# Import services
from ..services import storage # Use storage service for file I/O
# Import UI components (if needed) and FastHTML components
from fasthtml.common import Button, Div, Form, Input, P, Textarea, Br, H1, H2, Script, Title, Main, Header, Section, Style # NotStr removed as not used
# Import helpers from other modules if needed
from .routes_calendar import generate_calendar # Need calendar for redirect after save
from ..ui.components import _generate_sidebar, _generate_breadcrumbs # ADDED _generate_breadcrumbs import
# ------------------------------------------ #

# Task Editor View
@app.get("/edit-tasks/{day_name}")
def edit_tasks_view(request: Request, day_name: str):
    day_name_capitalized = day_name.capitalize() # Use a variable

    # Centralized error handling return for full page or fragment
    def _return_error(message: str):
        error_content = Div(P(message),
                           Button("Back to Calendar", hx_get="/",
                                  hx_target=config.MAIN_CONTENT_ID, hx_swap="innerHTML",
                                  hx_push_url="true",
                                  cls="button-back"),
                           id="task-editor-error") # Use consistent ID like task-editor
        
        if "hx-request" not in request.headers:
            sidebar = _generate_sidebar()
            main_content = Div(error_content, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
            return Title(f"Error Editing Tasks"), \
                   Div(Div(sidebar, main_content, cls="layout-container"))
        else:
            return error_content # Return only the error div for HTMX swap

    if day_name_capitalized not in config.DAYS_OF_WEEK:
        return _return_error(f"Invalid day name: {day_name}")

    # --- Smart pre-fill logic --- #
    current_tasks_content = None
    today_date_obj = datetime.date.today()
    today_date_str = today_date_obj.strftime("%Y-%m-%d")
    today_day_name = today_date_obj.strftime("%A").lower()

    if day_name.lower() == today_day_name:
        # Attempt 1: Load from today's specific daily file's task section if it matches the template day being edited.
        daily_content_parts = storage.read_notes_file(today_date_str) # Read full file
        if daily_content_parts is not None:
            parts = daily_content_parts.split(config.NOTES_SEPARATOR, 1)
            if len(parts) == 2 and parts[0].strip(): # Check if task part exists and is not empty
                current_tasks_content = parts[0].strip()
    
    if current_tasks_content is None:
        # Attempt 2: Fallback to the standard template file for the given day_name.
        current_tasks_content = storage.read_tasks_template(day_name)
    # --- End smart pre-fill logic --- #

    if current_tasks_content is None: # Handle case where no content found after all checks
         return _return_error(f"Error loading tasks for {day_name_capitalized}. No data found in daily file or template.")

    # Original form remains the same
    task_form = Form(
        Textarea(current_tasks_content or "", name="tasks_content", rows=15, cols=80, cls="task-editor-textarea"),
        Br(),
        Div(
            Input(type="submit", value="Save Tasks Template",
                    hx_post=f'/save-tasks/{day_name}',
                    hx_target=config.MAIN_CONTENT_ID,
                    hx_swap=f'innerHTML swap:{config.SWAP_DELAY_MS}ms',
                    style="width: 100%; margin-right: 0;",
                    ),
            cls="task-button-container"
        ),
        action="javascript:void(0);" # Keep this to prevent default form submission
    )

    # New structure for the editor content, mimicking personalize page
    breadcrumbs = _generate_breadcrumbs([
        ("Home", "/"),
        (f"Edit {day_name_capitalized} Template", None) # Current page
    ])

    styled_editor_content = Main(
        breadcrumbs, # Added breadcrumbs
        Header(H1(f"Edit Tasks Template: {day_name_capitalized}", cls="page-title"), cls="page-header"),
        Section(
            P(f"Define the default tasks for any {day_name_capitalized}.", cls="page-description"), # Added a description
            task_form, # The existing form
            cls="tasks-options" # Similar to personalize-options for consistent section styling if needed
        ),
        id=f"task-editor-content-{day_name.lower()}", # Unique ID for the page content
        cls="main-content-area" # Class for padding and background from personalize.css
    )

    # Link to personalize.css for the styles
    linked_css = Style("", src="/static/css/personalize.css")
    page_title = Title(f"Edit Tasks: {day_name_capitalized}")

    # Return full page or just fragment
    if "hx-request" not in request.headers:
        sidebar = _generate_sidebar()
        # Wrap the styled_editor_content in the main content container for full page loads.
        # The ID MAIN_CONTENT_ID is applied to this outer Div for full page context.
        # The styled_editor_content itself has cls="main-content-area" for styling consistency.
        full_page_main_content = Div(styled_editor_content, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
        return page_title, linked_css, Div(Div(sidebar, full_page_main_content, cls="layout-container"))
    else:
        # For HTMX requests, return the title, CSS link, and the new styled content directly.
        # This content will be swapped into the element with MAIN_CONTENT_ID.
        return page_title, linked_css, styled_editor_content

# Task Saving Action
@app.post("/save-tasks/{day_name}")
def save_tasks_action(day_name: str, tasks_content: str):
    error_msg = None
    success_msg = None
    msg_id = f"msg-{uuid.uuid4()}"

    if day_name.capitalize() not in config.DAYS_OF_WEEK:
        error_msg = f"Invalid day name: {day_name} for saving."
    else:
        # Use storage service to write
        success = storage.write_tasks_template(day_name, tasks_content)
        if success:
            success_msg = f"Tasks template for {day_name.capitalize()} saved successfully!"
        else:
            error_msg = f"Error saving tasks template for {day_name.capitalize()}."

    # Return Calendar View + Feedback
    now = datetime.datetime.now()
    calendar_content = generate_calendar(now.year, now.month) # Use helper from routes_calendar
    main_content_children = [calendar_content]

    message_div = None
    script_tag = None
    if success_msg or error_msg:
        msg_text = success_msg if success_msg else error_msg
        is_success = bool(success_msg)
        msg_class = "success-msg" if is_success else "error-msg"
        feedback_style_class = "feedback-block" # Use block style 
        
        # Create the block div - initially hidden
        message_div = Div(P(msg_text), 
                          cls=f"feedback-msg {feedback_style_class} {msg_class}", # No 'visible'
                          id=msg_id
                         )
        
        # Script to add .visible, then add .fade-out after delay
        script_content = f"""
            (function() {{
                var el = document.getElementById('{msg_id}');
                if (el) {{
                    requestAnimationFrame(() => {{
                        el.classList.add('visible');
                        setTimeout(() => {{
                            el.classList.add('fade-out');
                        }}, 1000); // Timeout 1s
                    }});
                }}
            }})();
        """
        script_tag = Script(script_content)

    if message_div:
        main_content_children.insert(0, message_div)
        if script_tag:
            main_content_children.insert(1, script_tag)

    # --- Add scroll-to-top script for mobile --- #
    scroll_script_content = """
        if (window.innerWidth <= 768) {
            window.scrollTo(0, 0);
        }
    """
    scroll_script_tag = Script(scroll_script_content)
    main_content_children.append(scroll_script_tag) # Append ensures it runs after DOM updates
    # ----------------------------------------- #

    # Return the main content area structure
    return Div(*main_content_children, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")

# Server route to handle checkbox toggle
@app.post("/toggle-task/{date_str}/{idx}")
def toggle_task(date_str: str, idx: int, checked: str):
    # Use storage service to toggle
    success = storage.toggle_task_in_notes(date_str, idx)
    if not success:
        # Error logged within storage function, maybe return specific error code?
        pass # Decide on error handling - maybe return 404 or 500?
    
    # Return empty string (like 204 No Content)
    return "" 