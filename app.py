import datetime
import os
import mistune # Import mistune for Markdown rendering
import calendar # Import calendar module
from starlette.staticfiles import StaticFiles # Re-add StaticFiles import
from starlette.requests import Request # Import Request for query params
from starlette.responses import RedirectResponse # For redirects if needed
import uuid # Import uuid for unique IDs

# Explicit imports - remove serve_static
from fasthtml.common import FastHTML, Link, Button, Div, Title, H1, H2, H3, P, Textarea, Form, Input, Hr, Br, Table , Tbody, Tr, Thead, Td, Span, A,Th,H4,Ul,Li, Script

app = FastHTML(
    hdrs=(
        Link(rel='stylesheet', href='/static/style.css'),
        # Add HTMX library if not included by default in your FastHTML version
        # Script(src="https://unpkg.com/htmx.org@1.9.10"),
        )
)

# Mount the static directory explicitly onto the app object
app.mount("/static", StaticFiles(directory="static"), name="static")

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SHORT_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Helper function for SIDEBAR day buttons
def create_sidebar_day_button(day):
    # Target the main content area to load the task editor
    return Li(Button(day, # Changed from Button to A or styled Button/Li
                     hx_get=f'/edit-tasks/{day.lower()}', # Points to NEW task editor route
                     hx_target='#main-content-area', # Target the main content div
                     hx_swap='innerHTML swap:322ms', # ADJUSTED SWAP DELAY
                     cls='sidebar-button' # New class for sidebar buttons
                    ))

# Updated Helper function to generate the calendar HTML + Controls
def generate_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    today = datetime.date.today()
    current_dt = datetime.date(year, month, 1)
    today_str = today.strftime("%Y-%m-%d") # Get today's date string

    # Calculate previous and next month/year
    prev_month_dt = current_dt - datetime.timedelta(days=1)
    prev_year, prev_month = prev_month_dt.year, prev_month_dt.month
    # Add ~35 days to estimate next month start, then get month/year
    next_month_dt_est = current_dt + datetime.timedelta(days=35)
    next_year, next_month = next_month_dt_est.year, next_month_dt_est.month

    # Controls
    controls = Div(
        A("< Prev", href=f"/?year={prev_year}&month={prev_month}", cls="cal-nav",
          hx_get=f"/?year={prev_year}&month={prev_month}", hx_target="#content-swap-wrapper", hx_swap="outerHTML swap:322ms", hx_push_url="true"),
        Span(f"{current_dt.strftime('%B %Y')}", cls="cal-month-year"),
        A("Next >", href=f"/?year={next_year}&month={next_month}", cls="cal-nav",
          hx_get=f"/?year={next_year}&month={next_month}", hx_target="#content-swap-wrapper", hx_swap="outerHTML swap:322ms", hx_push_url="true"),
        cls="calendar-controls"
    )

    # Calendar Table Generation (logic mostly same, ensure Td targets correct place)
    header_row = Tr(*[Th(day) for day in SHORT_DAYS], cls='calendar-header')
    weeks = []
    for week in cal:
        row = []
        for day_num in week:
            cell_cls = "calendar-cell"
            day_content_children = []
            htmx_attrs = {}
            if day_num == 0:
                cell_cls += " empty"
            else:
                current_date = datetime.date(year, month, day_num)
                date_str = current_date.strftime("%Y-%m-%d")
                cell_cls += " active"
                if current_date == today:
                    cell_cls += " today"
                day_content_children = [Span(str(day_num), cls='day-number')]
                htmx_attrs = {
                    'hx_get': f'/date/{date_str}',
                    'hx_target': '#content-swap-wrapper', # Target wrapper
                    'hx_swap': 'outerHTML swap:322ms' # Replace wrapper, with delay
                }
            row.append(Td(*day_content_children, cls=cell_cls, **htmx_attrs))
        weeks.append(Tr(*row))

    calendar_table = Table(Thead(header_row), Tbody(*weeks), cls='calendar-grid')

    # Return controls and table WRAPPED in the swappable div
    return Div(controls, calendar_table, id="content-swap-wrapper")

# Root route - handles optional year/month for calendar display
@app.get("/")
def home(request: Request):
    try:
        year = int(request.query_params.get("year", datetime.datetime.now().year))
        month = int(request.query_params.get("month", datetime.datetime.now().month))
        # Basic validation
        if not (1 <= month <= 12):
             month = datetime.datetime.now().month
             year = datetime.datetime.now().year # Reset year if month is invalid
    except ValueError:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month

    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")

    # Generate Sidebar Links and Today button
    sidebar_links = [create_sidebar_day_button(day) for day in DAYS_OF_WEEK]
    # Create Today button element
    today_button = Div(A("Today's Details", href="#", cls="sidebar-today-button",
                       hx_get=f"/date/{today_str}",
                       hx_target="#content-swap-wrapper", # Target main area's swap wrapper
                       hx_swap="outerHTML swap:322ms"
                      ), cls="sidebar-today-container")

    sidebar = Div(
        today_button, # Add Today button here
        H3("Week Tasks", cls="sidebar-title"),
        Ul(*sidebar_links, cls="sidebar-nav"),
        id="sidebar", cls="sidebar"
    )

    # Generate Calendar View - it now returns the #content-swap-wrapper
    calendar_content = generate_calendar(year, month)

    # Assemble main content area - initially just the calendar wrapper
    main_content = Div(
        calendar_content,
        # REMOVED initial details placeholder
        id="main-content-area", cls="main-content"
    )

    # Full page structure for initial load
    if "hx-request" not in request.headers:
        return Title("Weekly Task Notes"), \
               Div(
                   H1("Weekly Task Notes"),
                   Div( # Main layout container
                       sidebar,
                       main_content,
                       cls="layout-container"
                   )
               )
    else:
        # If HTMX request (Prev/Next), return only the new calendar content wrapper
        return calendar_content

# Task Editor View (Implemented)
@app.get("/edit-tasks/{day_name}")
def edit_tasks_view(day_name: str):
    day_name = day_name.lower()
    if day_name.capitalize() not in DAYS_OF_WEEK:
        # Handle invalid day name - maybe redirect or show error in main content
        # For simplicity, return an error message div
        return Div(P(f"Invalid day name: {day_name}"),
                   Button("Back to Calendar", hx_get="/", hx_target="#main-content-area", hx_swap="innerHTML"),
                   id="task-editor-error")

    # --- Load current tasks --- #
    tasks_file_path = os.path.join("tasks", f"{day_name}.md")
    current_tasks_content = ""
    if os.path.exists(tasks_file_path):
        try:
            with open(tasks_file_path, 'r', encoding='utf-8') as f:
                current_tasks_content = f.read()
        except OSError as e:
            print(f"Error reading task file {tasks_file_path} for editing: {e}")
            # Return error view if tasks can't be loaded
            return Div(P(f"Error loading tasks for {day_name.capitalize()}."),
                       Button("Back to Calendar", hx_get="/", hx_target="#main-content-area", hx_swap="innerHTML"),
                       id="task-editor-error")

    # --- Build Editor HTML --- #
    return Div(
        H2(f"Edit Tasks Template for {day_name.capitalize()}"),
        Form(
            Textarea(current_tasks_content, name="tasks_content", rows=15, cols=80, cls="task-editor-textarea"),
            Br(),
            Input(type="submit", value="Save Tasks Template",
                  hx_post=f'/save-tasks/{day_name}',
                  hx_target='#main-content-area',
                  hx_swap='innerHTML swap:322ms' # ADJUSTED SWAP DELAY
                 ),
            Button("Cancel / Back to Calendar",
                   hx_get="/",
                   hx_target="#main-content-area",
                   hx_swap="innerHTML swap:322ms", # ADJUSTED SWAP DELAY
                   cls="button-cancel"
                  ),
            action="javascript:void(0);"
        ),
        id="task-editor" # ID for the whole editor view
    )

# Task Saving Action (Remove placeholder)
@app.post("/save-tasks/{day_name}")
def save_tasks_action(day_name: str, tasks_content: str):
    day_name = day_name.lower()
    error_msg = None
    success_msg = None
    msg_id = f"msg-{uuid.uuid4()}" # Unique ID

    if day_name.capitalize() not in DAYS_OF_WEEK:
        error_msg = f"Invalid day name: {day_name} for saving."
    else:
        # Save content (existing logic)
        tasks_file_path = os.path.join("tasks", f"{day_name}.md")
        try:
            with open(tasks_file_path, 'w', encoding='utf-8') as f:
                f.write(tasks_content)
            success_msg = f"Tasks template for {day_name.capitalize()} saved successfully!"
        except OSError as e:
            print(f"Error saving tasks file {tasks_file_path}: {e}")
            error_msg = f"Error saving tasks template for {day_name.capitalize()}."

    # --- Return Calendar View + Feedback --- #
    now = datetime.datetime.now()
    calendar_content = generate_calendar(now.year, now.month) # This is the #content-swap-wrapper
    # Start with just the calendar content
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
    # Now only contains the optional message/script and the calendar wrapper
    return Div(*main_content_children, id="main-content-area", cls="main-content")

# Date Detail Route (Updated wrapper and added Back button)
@app.get("/date/{date_str}")
def get_date_details(date_str: str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower()
    except ValueError:
        # Return error wrapped in the target ID div
        return Div(P("Invalid date format.", cls="error-msg"), id='content-swap-wrapper')

    # --- Load CURRENT Tasks Template (read-only display) ---
    # We display the current template, not the potentially outdated one saved in the notes file
    tasks_file_path = os.path.join("tasks", f"{day_name}.md")
    tasks_display_html = ""
    if os.path.exists(tasks_file_path):
        try:
            with open(tasks_file_path, 'r', encoding='utf-8') as f:
                tasks_markdown = f.read()
                tasks_display_html = mistune.html(tasks_markdown)
        except OSError as e:
            print(f"Error reading task file {tasks_file_path} for display: {e}")
            tasks_display_html = P(f"Could not load tasks template for {day_name.capitalize()}.")
    else:
        tasks_display_html = P(f"No predefined tasks template for {day_name.capitalize()}.")

    # --- Load and PARSE Notes --- #
    notes_file_path = os.path.join("data", f"{date_str}_notes.md")
    notes_for_editing = "" # Content for the textarea
    full_saved_content = "" # For potential display if needed
    notes_separator = "\n\n---\n\n## My Notes\n\n"

    if os.path.exists(notes_file_path):
        try:
            with open(notes_file_path, 'r', encoding='utf-8') as f:
                full_saved_content = f.read()
            # Try to split the content
            parts = full_saved_content.split(notes_separator, 1)
            if len(parts) == 2:
                # Found separator, notes are the second part
                notes_for_editing = parts[1]
            else:
                # Separator not found, assume old format or notes only
                # Check if it starts with the tasks header (unlikely if saved by new code)
                if full_saved_content.startswith(f"## Tasks for {day_name.capitalize()}"):
                     # It might be an old file before the separator was added.
                     # It's hard to reliably extract just notes here.
                     # Safest is to put all content in textarea for user to fix.
                     print(f"Warning: Note file {notes_file_path} might be in old format.")
                     notes_for_editing = full_saved_content
                else:
                    # Assume it only contains notes
                    notes_for_editing = full_saved_content
        except OSError as e:
            print(f"Error reading notes file {notes_file_path}: {e}")
            # Potentially show an error message here?
            notes_for_editing = "Error loading saved notes."

    # --- Determine if editable --- #
    today = datetime.date.today()
    is_editable = (date_obj <= today)

    # --- Build HTML Response wrapped in #content-swap-wrapper ---
    details_children = [
        # Add a Back button
        Div(Button("< Back to Calendar",
                   hx_get="/", # Go back to root, which will render current month calendar
                   hx_target="#content-swap-wrapper",
                   hx_swap="outerHTML swap:322ms",
                   cls="button-back" # New class for styling
                  ), cls="back-button-container"),

        H3(f"{date_obj.strftime('%A, %B %d, %Y')}"),
        H4("Tasks"),
        Div(tasks_display_html if isinstance(tasks_display_html, str) else tasks_display_html, cls="tasks-display-readonly"),
        Hr(),
        H4("My Notes"),
        Form(
            Textarea(notes_for_editing, name="notes", rows=10, cols=80, disabled=not is_editable),
            Br(),
            Input(type="submit", value="Save Notes", disabled=not is_editable,
                  hx_post=f'/save-date/{date_str}',
                  hx_target='#content-swap-wrapper', # Target wrapper on save response
                  hx_swap='outerHTML' # Replace with updated details view (no delay needed on save response)
                 ) if is_editable else P("Notes can only be added/edited on or after the selected date."),
            action="javascript:void(0);"
        )
    ]
    # Wrap the details in the swappable div
    return Div(*details_children, id='content-swap-wrapper')

# Save Date Notes Route (UPDATED return structure)
@app.post("/save-date/{date_str}")
def save_date_notes(date_str: str, notes: str):
    error_msg = None
    success_msg = None
    msg_id = f"msg-{uuid.uuid4()}" # Unique ID for the message

    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower()
    except ValueError:
        # No fade-out needed for immediate error return
        return Div(P("Invalid date format.", cls="error-msg"), id='content-swap-wrapper')

    # Re-check if editable
    today = datetime.date.today()
    if date_obj > today:
        error_msg = "Cannot save notes for a future date."
        # Fall through to return get_date_details with the error message
    else:
        # Proceed with saving
        tasks_markdown_content = ""
        tasks_file_path = os.path.join("tasks", f"{day_name}.md")
        if os.path.exists(tasks_file_path):
            try:
                with open(tasks_file_path, 'r', encoding='utf-8') as f:
                    tasks_markdown_content = f.read()
            except OSError as e:
                print(f"Error reading task file {tasks_file_path}: {e}")
                error_msg = "Error reading tasks template; notes saved without tasks."
                # Continue saving just the notes

        final_content = f"## Tasks for {day_name.capitalize()}\n\n{tasks_markdown_content}\n\n---\n\n## My Notes\n\n{notes}"
        notes_file_path = os.path.join("data", f"{date_str}_notes.md")
        try:
            with open(notes_file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            success_msg = "Notes saved successfully!"
        except OSError as e:
            print(f"Error saving notes file {notes_file_path}: {e}")
            error_msg = "Error saving notes. Please try again."

    # --- Get Updated Details View --- #
    details_content_wrapper = get_date_details(date_str) # This is the Div id='content-swap-wrapper'

    # --- Prepare Feedback Elements (if any) --- #
    message_div = None
    script_tag = None
    if success_msg or error_msg:
        msg_text = success_msg if success_msg else error_msg
        msg_class = "success-msg" if success_msg else "error-msg"
        msg_id = f"msg-{uuid.uuid4()}"
        message_div = Div(P(msg_text), cls=f"feedback-msg {msg_class}", id=msg_id)
        script_tag = Script(f"setTimeout(() => document.getElementById('{msg_id}')?.classList.add('fade-out'), 1000)")

    # --- Return Feedback + Content --- #
    if message_div:
        # Return message, script, and the main content wrapper as siblings
        return message_div, script_tag if script_tag else "", details_content_wrapper
    else:
        # No message, just return the main content wrapper
        return details_content_wrapper

# Main entry point remains the same
if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("tasks", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 