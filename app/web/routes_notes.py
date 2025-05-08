import datetime
import os
import uuid

from starlette.requests import Request
from bs4 import BeautifulSoup

from ..main import app
from .. import config
from ..services import storage, markdown # Use storage service for file I/O, markdown for rendering
# Import UI components (if needed) and FastHTML components
from fasthtml.common import  Button, Div, Form,  P, Textarea, Br, H1,H2, H3, H4, Hr, Script, NotStr, Title
# Import sidebar helper
from ..ui.components import _generate_sidebar, day_nav_button # Import UI helpers
# ------------------------------------------ #

# --- Helper Functions for Date Detail View --- #

def _build_day_navigation(date_obj: datetime.date) -> Div:
    """Generates the navigation component for the day detail view."""
    # --- Calculate Nav Dates --- #
    prev_day = date_obj - datetime.timedelta(days=1)
    next_day = date_obj + datetime.timedelta(days=1)
    prev_week = date_obj - datetime.timedelta(weeks=1)
    next_week = date_obj + datetime.timedelta(weeks=1)
    prev_day_str = prev_day.strftime("%Y-%m-%d")
    next_day_str = next_day.strftime("%Y-%m-%d")
    prev_week_str = prev_week.strftime("%Y-%m-%d")
    next_week_str = next_week.strftime("%Y-%m-%d")

    # --- Build Nav Container --- #
    nav_container = Div(
        Button("< Back to Calendar",
               hx_get="/", 
               hx_target=config.MAIN_CONTENT_ID,
               hx_swap=f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
               hx_push_url="true",
               cls="button-back"
              ),
        day_nav_button("Last Week", prev_week_str),
        day_nav_button("Yesterday", prev_day_str),
        day_nav_button("Tomorrow", next_day_str), 
        day_nav_button("Next Week", next_week_str),
        cls="day-nav-container"
    )
    return nav_container

def _build_day_tasks(date_obj: datetime.date, date_str: str, day_name: str):
    """Generates the task-related components for the day detail view."""
    return ReadOnlyTasksBlock(date_obj, date_str, day_name) # Modified to call new component

def ReadOnlyTasksBlock(date_obj: datetime.date, date_str: str, day_name: str):
    """Generates the read-only display block for tasks with dblclick to edit."""
    raw_tasks_md = storage.read_raw_tasks(date_str, day_name)
    tasks_display_content: NotStr | P

    try:
        tasks_html_output = markdown.md_to_html(raw_tasks_md)
        soup = BeautifulSoup(tasks_html_output, 'html.parser')
        checkboxes = soup.select('li.task-list-item input.task-list-item-checkbox[type="checkbox"]')
        for idx, cb in enumerate(checkboxes):
            cb['data-idx'] = str(idx)
            cb['hx-post'] = f'/toggle-task/{date_str}/{idx}'
            cb['hx-trigger'] = 'change'
            cb['hx-swap'] = 'none' # Keep as none, toggle happens in backend
            is_checked_str = "true" if cb.has_attr("checked") else "false"
            # hx-vals is not strictly needed if the backend doesn't use it for toggle, but good for consistency
            cb['hx-vals'] = f'{{"checked": "{is_checked_str}"}}'
            if 'disabled' in cb.attrs: # Ensure checkboxes in display are not disabled
                del cb['disabled']
        modified_html_output = str(soup)
        tasks_display_content = NotStr(modified_html_output)
    except Exception as e:
        print(f"Error processing task markdown for ReadOnlyTasksBlock: {e}")
        tasks_display_content = P(f"Could not render tasks.")

    block_id = f"tasks-block-{date_str}"
    return Div(
        H2(f"{date_obj.strftime('%A, %B %d, %Y')}"), 
        H3("Tasks"), 
        Div(tasks_display_content, cls="tasks-display-readonly", **{'data-date-str': date_str}),
        Hr(),
        # HTMX attributes for double-click to edit
        id=block_id,
        cls="tasks-readonly-block hover-effect-glow", # Class for styling and targeting
        hx_get=f"/edit-day-tasks/{date_str}",
        hx_target="this",
        hx_swap="outerHTML transition:true",
        hx_trigger="dblclick"
    )

def TasksEditorForm(date_obj: datetime.date, date_str: str, day_name: str, raw_tasks_md: str, is_editable: bool):
    """Generates the tasks editor form component."""
    block_id = f"tasks-block-{date_str}" # Same ID as the read-only block for replacement
    form_children = [
        H3(f"{date_obj.strftime('%A, %B %d, %Y')}"), 
        H4("Tasks"),
        Textarea(raw_tasks_md, name="tasks_content", id="tasks-editor-textarea", 
                 disabled=not is_editable, style="height: 400px; width: 100%;"),
        Div(id="tasks-save-feedback-area", style="min-height: 30px;"), 
        Br()
    ]
    form_children.append(
        Button("Save Tasks", 
               type="button",
               disabled=False,
               hx_post=f'/save-day-tasks/{date_str}',
               hx_target=f"#{block_id}", # Target the block itself to replace form with new read-only view
               hx_swap='outerHTML transition:true', 
               hx_include='closest form',
               style="width: 100%; margin-right: 0;"
               )
    )

    return Form(
        *form_children,
        id=block_id, # Ensure the form has the same ID for replacement targeting
        action="javascript:void(0);",
        cls="tasks-editor-form"
    )

# --- Component for Read-Only Notes View --- #
def ReadOnlyNotesView(date_str: str, rendered_html: str):
    return Div(
        NotStr(rendered_html), # Display rendered HTML
        # Add HTMX attributes for double-click
        id=f"notes-view-{date_str}",
        cls="notes-readonly-view hover-effect-glow", # Class for styling
        hx_get=f"/edit-notes/{date_str}", # Endpoint to get the editor
        hx_target="this",
        hx_swap="outerHTML transition:true",
        hx_trigger="dblclick"
    )

# --- Component for Notes Editor Form (Reinstated) --- #
def NotesEditorForm(date_str: str, notes_content: str, is_editable: bool):
    """Generates the notes editor form component."""
    return Form(
        Textarea(notes_content, name="notes", id="notes-editor-textarea", 
                 disabled=not is_editable, style="height: 250px;"), # Original height
        Div(id="notes-save-feedback-area", style="min-height: 50px;"), 
        Br(),
        Button("Save Notes", 
               type="button",
               disabled=not is_editable,
               hx_post=f'/save-date/{date_str}',
               hx_target='#notes-save-feedback-area', 
               hx_swap='innerHTML scroll:false', 
               style="width: 100%; margin-right: 0;"
               )
        if is_editable else P("Notes cannot be edited for this date."),
        action="javascript:void(0);",
        cls="notes-editor-form"
    )

def _build_notes_component(date_obj: datetime.date, date_str: str):
    """Decides and builds the notes component (read-only or editor)."""
    today = datetime.date.today()
    is_editable = (date_obj <= today) # Check editability based on date
    
    notes_content_raw = storage.read_notes_for_editing(date_str)

    # Check if content exists AND is not just whitespace
    if notes_content_raw and notes_content_raw.strip():
        # Notes exist and have content: Render read-only view
        
        try:
            rendered_html = markdown.md_to_html(notes_content_raw)
            # Only return read-only if rendering succeeds
            return ReadOnlyNotesView(date_str, rendered_html)
        except Exception as e:
            print(f"Error rendering markdown for {date_str}: {e}")
            # Fallback to editor if rendering fails
            return NotesEditorForm(date_str, notes_content_raw, is_editable)
    else:
        # No notes OR notes are empty/whitespace: Return editor form
        # Ensure we pass an empty string if content is None or empty
        content_for_editor = notes_content_raw if notes_content_raw is not None else ""
        return NotesEditorForm(date_str, content_for_editor, is_editable)

# --- End Helper Functions --- #


# --- Main Route - Renamed to /view-day --- #
@app.get("/view-day/{date_str}") # Renamed route
def get_date_details_view(request: Request, date_str: str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower()
    except ValueError:
        return Div(P("Invalid date format.", cls="error-msg"), id=config.CONTENT_SWAP_ID.strip('#'))

    # Build the view components using helpers
    nav_component = _build_day_navigation(date_obj)
    task_components = _build_day_tasks(date_obj, date_str, day_name)
    notes_part = _build_notes_component(date_obj, date_str)
    
    
    
    # Combine children
    details_children = [
        nav_component,
        task_components,
        H1("My Notes"), 
        notes_part # This is either ReadOnlyNotesView or NotesEditorForm
    ]
    # --- Check if notes_part is the editor form based on its tag --- #
    needs_mde_init = hasattr(notes_part, 'tag') and notes_part.tag == 'form'
        
    # If MDE is needed, append the initialization script directly
    if needs_mde_init:
        # Use setTimeout to defer execution slightly after DOM update
        details_children.append(Script("setTimeout(initializeEasyMDE, 0);")) 
        
    details_content_wrapper = Div(*details_children, 
                                  id=config.CONTENT_SWAP_ID.strip('#'),
                                  cls="page-content-entry" # ADDED CLASS for entry animation
                                  # REMOVED **htmx_init_attrs
                                 )

    # Return full page or just fragment
    if "hx-request" not in request.headers:
        sidebar = _generate_sidebar()
        main_content = Div(details_content_wrapper, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
        return Title(f"Day View {date_str}"), \
               Div(Div(sidebar, main_content, cls="layout-container"))
    else:
        return details_content_wrapper
# --- End Main Route --- #

# --- NEW: Endpoint to specifically return the editor --- #
@app.get("/edit-notes/{date_str}")
def get_notes_editor_component(date_str: str):
    """Returns only the notes editor component (triggered by dblclick)."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return P("Invalid date.", cls="error-msg")
        
    today = datetime.date.today()
    is_editable = (date_obj <= today)
    notes_content = storage.read_notes_for_editing(date_str) or ""
    
    # Return ONLY the form component, ready for swapping
    editor_form = NotesEditorForm(date_str, notes_content, is_editable)
    # --- REVERT to direct script append --- #
    # Add the initialization script directly after the form
    # Use setTimeout to defer execution slightly after DOM update
    return editor_form, Script("setTimeout(initializeEasyMDE, 0);")
    
# --- End Editor Endpoint --- #

# --- Task Editing Endpoints --- #
@app.get("/edit-day-tasks/{date_str}")
def get_tasks_editor_component(request: Request, date_str: str):
    """Returns only the tasks editor component."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower() # Needed for TasksEditorForm
    except ValueError:
        return P("Invalid date for tasks editor.", cls="error-msg")
        
    today = datetime.date.today()

    raw_tasks_md = storage.read_raw_tasks(date_str, day_name)
    
    editor_form = TasksEditorForm(date_obj, date_str, day_name, raw_tasks_md, True)
    # Append the script to initialize the *tasks* MDE instance
    return editor_form, Script("setTimeout(initializeTasksMDE, 0);")

@app.post("/save-day-tasks/{date_str}")
def save_tasks_content(request: Request, date_str: str, tasks_content: str):
    """Saves the updated tasks markdown and returns the ReadOnlyTasksBlock."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower()
    except ValueError:
        # Consider returning an error message that can be displayed in a feedback area
        return P("Invalid date for saving tasks.", cls="error-msg")

    print(f"--- ROUTES: save_tasks_content for {date_str} ---")

    # Add any validation for tasks_content if needed here
    today = datetime.date.today()
    force_notes_reset = date_obj > today
    
    success = storage.save_raw_tasks(date_str, day_name, tasks_content, force_empty_notes=force_notes_reset)
    print(f"storage.save_raw_tasks returned: {success}")
    
    if success:
        # Return the updated read-only block for HTMX to swap
        return ReadOnlyTasksBlock(date_obj, date_str, day_name)
    else:
        # How to handle save failure? For now, return a simple message.
        # Ideally, the TasksEditorForm would have a feedback area like notes.
        # We can enhance this later.
        # For now, returning the form again with an error might be too complex for current setup.
        return Div(P("Error saving tasks. Please try again.", cls="error-msg"), 
                   id=f"tasks-block-{date_str}" # Ensure it replaces the form
                  ) 

# --- Save Date Notes Route (Remains largely the same) --- #
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

# --- Toggle Task Route (Remains the same) --- #
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