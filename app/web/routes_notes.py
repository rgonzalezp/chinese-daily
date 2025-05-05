import datetime
import os
import uuid

from starlette.requests import Request
from bs4 import BeautifulSoup

from ..main import app
from .. import config
from ..services import storage, markdown # Use storage service for file I/O, markdown for rendering
# Import UI components (if needed) and FastHTML components
from fasthtml.common import A, Button, Div, Form, Input, P, Textarea, Br, H1, H3, H4, Hr, Script, NotStr, Title, Span
# Import sidebar helper
from ..ui.components import _generate_sidebar, day_nav_button # Import UI helpers
# ------------------------------------------ #

# --- Helper Functions for Date Detail View --- #

def _build_day_tasks_and_nav(date_obj: datetime.date, date_str: str, day_name: str):
    """Generates the top part of the day detail view (Nav, Tasks)."""
    # --- Get Task Markdown --- #
    tasks_markdown_source = storage.read_tasks_for_display(date_str, day_name)
    
    # --- Render Tasks --- #
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

    # --- Calculate Nav Dates --- #
    prev_day = date_obj - datetime.timedelta(days=1)
    next_day = date_obj + datetime.timedelta(days=1)
    prev_week = date_obj - datetime.timedelta(weeks=1)
    next_week = date_obj + datetime.timedelta(weeks=1)
    prev_day_str = prev_day.strftime("%Y-%m-%d")
    next_day_str = next_day.strftime("%Y-%m-%d")
    prev_week_str = prev_week.strftime("%Y-%m-%d")
    next_week_str = next_week.strftime("%Y-%m-%d")

    # --- Build Nav Container and Tasks Display --- #
    nav_container = Div(
        Button("< Back to Calendar",
               hx_get="/", hx_target=config.CONTENT_SWAP_ID,
               hx_swap=f"outerHTML swap:{config.SWAP_DELAY_MS}ms", 
               hx_push_url="true",
               cls="button-back"
              ),
        day_nav_button("Last Week", prev_week_str),
        day_nav_button("Yesterday", prev_day_str),
        day_nav_button("Tomorrow", next_day_str), 
        day_nav_button("Next Week", next_week_str),
        cls="day-nav-container"
    )
    
    tasks_display_div = Div(tasks_display_content, 
                            cls="tasks-display-readonly", 
                            **{'data-date-str': date_str}
                           )
                           
    return [nav_container, H3(f"{date_obj.strftime('%A, %B %d, %Y')}"), H4("Tasks"), tasks_display_div, Hr()]

# Placeholder for ReadOnlyNotesView component we'll create in Step 3
def ReadOnlyNotesView(date_str: str, rendered_html: str):
    return Div(
        NotStr(rendered_html), # Display rendered HTML
        # Add HTMX attributes for double-click
        id=f"notes-view-{date_str}",
        cls="notes-readonly-view", # Class for styling
        hx_get=f"/edit-notes/{date_str}", # Endpoint to get the editor
        hx_target="this",
        hx_swap="outerHTML transition:true",
        hx_trigger="dblclick"
    )

def NotesEditorForm(date_str: str, notes_content: str, is_editable: bool):
    """Generates the notes editor form component."""
    return Form(
        Textarea(notes_content, name="notes", id="notes-editor-textarea", 
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
        if is_editable else P("Notes cannot be edited for this date."),
        action="javascript:void(0);"
     , cls="notes-editor-form")

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
        print(f"--- Debug: notes_content_raw={notes_content_raw} ---")
        content_for_editor = notes_content_raw if notes_content_raw is not None else ""
        print(f"--- Debug: content_for_editor={content_for_editor} ---")
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
    top_part = _build_day_tasks_and_nav(date_obj, date_str, day_name)
    notes_part = _build_notes_component(date_obj, date_str)
    
    
    
    # Combine children
    details_children = [
        *top_part,
        H4("My Notes"), 
        notes_part # This is either ReadOnlyNotesView or NotesEditorForm
    ]
    print(f"--- Debug: notes_part={notes_part} ---")
    # --- Check if notes_part is the editor form based on its tag --- #
    needs_mde_init = hasattr(notes_part, 'tag') and notes_part.tag == 'form'
        
    # If MDE is needed, append the initialization script directly
    if needs_mde_init:
        # Use setTimeout to defer execution slightly after DOM update
        details_children.append(Script("setTimeout(initializeEasyMDE, 0);")) 
        
    details_content_wrapper = Div(*details_children, 
                                  id=config.CONTENT_SWAP_ID.strip('#')
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