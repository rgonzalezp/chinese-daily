import datetime
import uuid
import os

from starlette.requests import Request # Needed if used, maybe not here

# Assuming this file is in app/web/, import app from app/main.py
# --- Make imports relative to app package --- #
from ..main import app
from .. import config
# Import services
from ..services import storage # Use storage service for file I/O
# Import UI components (if needed) and FastHTML components
from fasthtml.common import Button, Div, Form, Input, P, Textarea, Br, H2, Script, NotStr # Add NotStr if needed? Maybe not here
# Import helpers from other modules if needed
from .routes_calendar import generate_calendar # Need calendar for redirect after save
# ------------------------------------------ #

# Task Editor View
@app.get("/edit-tasks/{day_name}")
def edit_tasks_view(day_name: str):
    if day_name.capitalize() not in config.DAYS_OF_WEEK:
        return Div(P(f"Invalid day name: {day_name}"),
                   Button("Back to Calendar", hx_get="/", 
                          hx_target=config.MAIN_CONTENT_ID, hx_swap="innerHTML",
                          hx_push_url="true",
                          cls="button-back"),
                   id="task-editor-error")

    current_tasks_content = storage.read_tasks_template(day_name)
    if current_tasks_content is None: # Handle potential read error if needed
         return Div(P(f"Error loading tasks for {day_name.capitalize()}."),
                   Button("Back to Calendar", hx_get="/", 
                          hx_target=config.MAIN_CONTENT_ID, hx_swap="innerHTML",
                          hx_push_url="true",
                          cls="button-back"),
                   id="task-editor-error")

    # Build Editor HTML
    return Div(
        H2(f"Edit Tasks Template for {day_name.capitalize()}"),
        Form(
            Textarea(current_tasks_content or "", name="tasks_content", rows=15, cols=80, cls="task-editor-textarea"),
            Br(),
            Input(type="submit", value="Save Tasks Template",
                  hx_post=f'/save-tasks/{day_name}',
                  hx_target=config.MAIN_CONTENT_ID, 
                  hx_swap=f'innerHTML swap:{config.SWAP_DELAY_MS}ms'
                 ),
            Button("Cancel / Back to Calendar",
                   hx_get="/",
                   hx_target=config.MAIN_CONTENT_ID,
                   hx_swap=f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
                   hx_push_url="true",
                   cls="button-cancel"
                  ),
            action="javascript:void(0);"
        ),
        id="task-editor"
    )

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
        msg_class = "success-msg" if success_msg else "error-msg"
        message_div = Div(P(msg_text), cls=f"feedback-msg {msg_class}", id=msg_id)
        script_tag = Script(f"setTimeout(() => document.getElementById('{msg_id}')?.classList.add('fade-out'), 1000)")

    if message_div:
        main_content_children.insert(0, message_div)
        if script_tag:
            main_content_children.insert(1, script_tag)

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