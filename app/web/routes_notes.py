import datetime
import os
import uuid

from starlette.requests import Request
from bs4 import BeautifulSoup

# Assuming this file is in app/web/, import app from app/main.py
# --- Make imports relative to app package --- #
from ..main import app
from .. import config
from ..services import storage, markdown # Use storage service for file I/O, markdown for rendering
# Import UI components (if needed) and FastHTML components
from fasthtml.common import A, Button, Div, Form, Input, P, Textarea, Br, H1, H3, H4, Hr, Script, NotStr, Title, Span
# Import sidebar helper
from ..ui.components import _generate_sidebar, day_nav_button # Import UI helpers
# ------------------------------------------ #

# Date Detail Route
@app.get("/date/{date_str}")
def get_date_details(request: Request, date_str: str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower()
    except ValueError:
        return Div(P("Invalid date format.", cls="error-msg"), id=config.CONTENT_SWAP_ID.strip('#'))

    # --- Get Task Markdown (uses storage service) --- #
    tasks_markdown_source = storage.read_tasks_for_display(date_str, day_name)
    
    # --- Render Tasks (uses markdown service, BeautifulSoup) --- #
    tasks_display_content: NotStr | P
    try:
        tasks_html_output = markdown.md_to_html(tasks_markdown_source)
        soup = BeautifulSoup(tasks_html_output, 'html.parser')
        checkboxes = soup.select('li.task-list-item input.task-list-item-checkbox[type="checkbox"]')
        for idx, cb in enumerate(checkboxes):
            cb['data-idx'] = str(idx)
            cb['hx-post'] = f'/toggle-task/{date_str}/{idx}'
            cb['hx-trigger'] = 'change'
            cb['hx-swap'] = 'none'
            is_checked_str = "true" if cb.has_attr("checked") else "false"
            cb['hx-vals'] = f'{{"checked": "{is_checked_str}"}}'
            if 'disabled' in cb.attrs:
                del cb['disabled']
        modified_html_output = str(soup)
        tasks_display_content = NotStr(modified_html_output)
    except Exception as e:
        print(f"Error processing task markdown: {e}")
        tasks_display_content = P(f"Could not render tasks.")
        
    # --- Load Notes for Editor (uses storage service) --- #
    notes_for_editing = storage.read_notes_for_editing(date_str)

    # --- Determine if editable --- #
    today = datetime.date.today()
    is_editable = (date_obj <= today)

    # --- Calculate Nav Dates --- #
    prev_day = date_obj - datetime.timedelta(days=1)
    next_day = date_obj + datetime.timedelta(days=1)
    prev_week = date_obj - datetime.timedelta(weeks=1)
    next_week = date_obj + datetime.timedelta(weeks=1)
    prev_day_str = prev_day.strftime("%Y-%m-%d")
    next_day_str = next_day.strftime("%Y-%m-%d")
    prev_week_str = prev_week.strftime("%Y-%m-%d")
    next_week_str = next_week.strftime("%Y-%m-%d")

    # --- Build Detail Content Wrapper --- #
    details_children = [
        Div(
            Button("< Back to Calendar",
                   hx_get="/", hx_target=config.CONTENT_SWAP_ID,
                   hx_swap=f"outerHTML swap:{config.SWAP_DELAY_MS}ms", 
                   hx_push_url="true",
                   cls="button-back"
                  ),
            # --- Use UI Helper for nav buttons --- #
            day_nav_button("Last Week", prev_week_str),
            day_nav_button("Yesterday", prev_day_str),
            day_nav_button("Tomorrow", next_day_str), 
            day_nav_button("Next Week", next_week_str),
            # ----------------------------------- #
            cls="day-nav-container"
        ),
        H3(f"{date_obj.strftime('%A, %B %d, %Y')}"),
        H4("Tasks"),
        Div(tasks_display_content, 
            cls="tasks-display-readonly", 
            **{'data-date-str': date_str}
           ),
        Hr(),
        # Restore H4 to original state
        H4("My Notes"), 
        # Remove Span and Div wrapper
        Form(
            Textarea(notes_for_editing, name="notes", id="notes-editor-textarea", 
                     disabled=not is_editable, style="height: 250px;"),
            # Restore feedback Div location & ID, add min-height
            Div(id="notes-save-feedback-area", style="min-height: 50px;"), 
            Br(),
            Button("Save Notes", 
                   type="button", # Prevent default submit
                   disabled=not is_editable,
                   hx_post=f'/save-date/{date_str}',
                   hx_target='#notes-save-feedback-area', 
                   hx_swap='innerHTML scroll:false', 
                   style="width: 100%; margin-right: 0;" # Keep style
                   )
            if is_editable else P("Notes can only be added/edited on or after the selected date."),
            # Keep action javascript:void(0) on form as extra safety? Optional.
            action="javascript:void(0);"
         , cls="notes-editor-form"),
    ]
    details_content_wrapper = Div(*details_children, 
                                  id=config.CONTENT_SWAP_ID.strip('#'),
                                  hx_trigger="load", 
                                  **{"hx-on::load": "initializeEasyMDE()"})

    # Return full page or just fragment
    if "hx-request" not in request.headers:
        sidebar = _generate_sidebar()
        main_content = Div(details_content_wrapper, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
        return Title(f"Notes for {date_str}"), \
               Div(

                   Div(sidebar, main_content, cls="layout-container")
               )
    else:
        return details_content_wrapper

# Save Date Notes Route
@app.post("/save-date/{date_str}")
def save_date_notes(date_str: str, notes: str):
    error_msg = None
    success_msg = None

    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower()
    except ValueError:
        msg_id = f"msg-{uuid.uuid4()}"
        message_div = Div(P("Invalid date format.", cls="error-msg"), cls=f"feedback-msg error-msg", id=msg_id)
        script_tag = Script(f"setTimeout(() => document.getElementById('{msg_id}')?.classList.add('fade-out'), 1000)")
        return message_div, script_tag

    today = datetime.date.today()
    if date_obj > today:
        error_msg = "Cannot save notes for a future date."
    else:
        # Use storage service to save
        success = storage.save_full_notes_content(date_str, day_name, notes)
        if success:
            success_msg = "Notes saved successfully!"
        else:
             error_msg = "Error saving notes. Please try again."

    # Prepare Feedback Elements
    message_div = None
    script_tag = None
    if success_msg or error_msg:
        msg_text = success_msg if success_msg else error_msg
        is_success = bool(success_msg)
        msg_class = "success-msg" if is_success else "error-msg"
        feedback_style_class = "feedback-block" # Use block style for now
        msg_id = f"msg-{uuid.uuid4()}"
        
        # Create the feedback div - initially hidden
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
                        }}, 1000); // Timeout back to 1s
                    }});
                }}
            }})();
        """
        script_tag = Script(script_content)

    # Return ONLY Feedback Div + Script
    if message_div:
        return message_div, script_tag if script_tag else ""
    else:
        return ""

# Toggle Task Route
@app.post("/toggle-task/{date_str}/{idx}")
async def toggle_task(date_str: str, idx: int):
    """Handles checkbox toggle POST requests. Ignores request body."""
    try:
        # Validate index is non-negative
        if idx < 0:
            print(f"Error toggle_task route: Invalid negative index {idx} received for {date_str}.")
            return # Don't proceed
            
        # Call the storage service function to perform the toggle
        success = storage.toggle_task_in_notes(date_str=date_str, task_index=idx)
        
        if success:
            print(f"--- Routes: Toggle successful for {date_str}, index {idx} (storage confirmed save). ---")
        else:
            # Error already printed within the service function
             print(f"--- Routes: Toggle FAILED for {date_str}, index {idx} (error logged by storage service). ---")
            
    except Exception as e:
        # Catch potential errors during processing
        print(f"Error in toggle_task route handler for {date_str}, index {idx}: {e}")

    # Important: Return empty response as hx-swap="none"
    return 