import datetime
import os
import mistune # Import mistune for Markdown rendering
import calendar # Import calendar module
from starlette.staticfiles import StaticFiles # Re-add StaticFiles import

# Explicit imports - remove serve_static
from fasthtml.common import FastHTML, Link, Button, Div, Title, H1, H2, P, Textarea, Form, Input, Hr, Br, Table , Tbody, Tr, Thead, Td, Span, A,Th,H3

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

# Helper function (optional, could be inline)
def create_day_button(day):
    return Button(day,
                  hx_get=f'/day/{day.lower()}',
                  hx_target='#day-details',
                  hx_swap='innerHTML',
                  cls='day-button' # Add a class for styling
                 )

# Helper function to generate the calendar HTML
def generate_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    today = datetime.date.today()

    header_row = Tr(*[Th(day) for day in SHORT_DAYS], cls='calendar-header')
    weeks = []
    for week in cal:
        row = []
        for day_num in week:
            cell_cls = "calendar-cell"
            day_content_children = []
            htmx_attrs = {}

            if day_num == 0: # Day is not in the current month
                cell_cls += " empty"
            else:
                current_date = datetime.date(year, month, day_num)
                date_str = current_date.strftime("%Y-%m-%d")
                cell_cls += " active"
                if current_date == today:
                    cell_cls += " today"

                # Only include the day number span
                day_content_children = [
                    Span(str(day_num), cls='day-number')
                ]

                # Define HTMX attributes for the cell
                htmx_attrs = {
                    'hx_get': f'/date/{date_str}',
                    'hx_target': '#day-details',
                    'hx_swap': 'innerHTML'
                }

            # Create the Td, applying HTMX attributes if it's an active day
            row.append(Td(*day_content_children, cls=cell_cls, **htmx_attrs))

        weeks.append(Tr(*row))

    return Table(
        Thead(header_row),
        Tbody(*weeks),
        cls='calendar-grid'
    )

# Updated Home Route
@app.get("/")
def home():
    top_day_buttons = [create_day_button(day) for day in DAYS_OF_WEEK]
    now = datetime.datetime.now()
    calendar_html = generate_calendar(now.year, now.month)

    return Title("Daily Planner"), \
           Div(
               H1("Weekly Planner"),
               # --- Top Weekday Buttons (Generic Tasks) ---
               Div(*top_day_buttons, id='weekday-selector', cls='weekday-container'),
               # --- Monthly Calendar (Specific Dates) ---
               Div(calendar_html, id='calendar-view', cls='calendar-container'), # Changed class
               # --- Area for Day Details ---
               Div(P("Click a day button or a calendar date."), id='day-details', cls='details-container'),
               id='main-container'
           )

# Adjusted Day Detail Route (for top buttons - shows template)
@app.get("/day/{day_name}")
def get_day_template(day_name: str):
    day_name = day_name.lower()
    if day_name.capitalize() not in DAYS_OF_WEEK:
        return P("Invalid day name.", id='day-details')

    # --- Load Tasks Template ---
    tasks_file_path = os.path.join("tasks", f"{day_name}.md")
    tasks_html = ""
    if os.path.exists(tasks_file_path):
        with open(tasks_file_path, 'r', encoding='utf-8') as f:
            tasks_markdown = f.read()
            tasks_html = mistune.html(tasks_markdown)
    else:
        tasks_html = P(f"No predefined tasks template for {day_name.capitalize()}.")

    # --- Build HTML Response (Template View) ---
    return Div(
        H2(f"{day_name.capitalize()} Task Template"),
        tasks_html if isinstance(tasks_html, str) else tasks_html, # Handle P object or HTML string
        Hr(),
        P("This shows the generic tasks. Click a date on the calendar to view/edit date-specific notes."),
        Button("Close", hx_get='/', hx_target='#main-container', hx_swap='innerHTML'),
        id='day-details'
    )

# NEW: Date Detail Route (Implemented)
@app.get("/date/{date_str}")
def get_date_details(date_str: str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date_obj.strftime('%A').lower() # Get day name for tasks
    except ValueError:
        return P("Invalid date format. Use YYYY-MM-DD.", id='day-details')

    # --- Load Tasks (Based on day of week) ---
    tasks_file_path = os.path.join("tasks", f"{day_name}.md")
    tasks_html = ""
    if os.path.exists(tasks_file_path):
        with open(tasks_file_path, 'r', encoding='utf-8') as f:
            tasks_markdown = f.read()
            tasks_html = mistune.html(tasks_markdown)
    else:
        tasks_component = P(f"No predefined tasks template for {day_name.capitalize()}.")

    # --- Load DATE-SPECIFIC Notes ---
    notes_file_path = os.path.join("data", f"{date_str}_notes.md") # Use YYYY-MM-DD_notes.md
    notes_content = ""
    if os.path.exists(notes_file_path):
        with open(notes_file_path, 'r', encoding='utf-8') as f:
            notes_content = f.read()

    # --- Determine if editable (Based on specific date) ---
    today = datetime.date.today()
    is_editable = (date_obj <= today)

    # --- Build HTML Response --- #
    response_children = [
        H2(f"{date_obj.strftime('%A, %B %d, %Y')}"), # Show full date
        H3("Tasks"), # Sub-heading for tasks
    ]
    if tasks_html:
        response_children.append(tasks_html)
    else:
        response_children.append(tasks_component)

    response_children.extend([
        Hr(),
        H3("My Notes"), # Sub-heading for notes
        Form(
            Textarea(notes_content, name="notes", rows=10, cols=80, disabled=not is_editable),
            Br(),
            Input(type="submit", value="Save Date Notes", disabled=not is_editable,
                  hx_post=f'/save-date/{date_str}', # Post to save-date route
                  hx_target='#day-details',
                  hx_swap='innerHTML' # Swap innerHTML to keep main Div intact
                 ) if is_editable else P("Notes can only be added/edited on or after the selected date."),
            Button("Close",
                   hx_get='/', # Go back to the main calendar view
                   hx_target='#main-container',
                   hx_swap='innerHTML'
                  ),
            action="javascript:void(0);"
        )
    ])

    return Div(*response_children, id='day-details')

# Adjusted Save Notes Route (Generic - currently disabled)
@app.post("/save/{day_name}")
def save_generic_notes(day_name: str, notes: str):
    # For now, let's prevent saving from the generic view
    # Could be repurposed later to save template notes if needed
    print(f"Attempted to save generic notes for {day_name} (currently disabled).")
    # Re-render the template view
    return get_day_template(day_name)

# NEW: Save Date Notes Route (Implemented)
@app.post("/save-date/{date_str}")
def save_date_notes(date_str: str, notes: str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return P("Invalid date format.", id='day-details')

    # --- Re-check if editable (Based on specific date) ---
    today = datetime.date.today()
    if date_obj > today:
        # Prevent saving to future dates
        print(f"Attempted to save notes for future date {date_str} (prevented).")
        # Return the current view for that date without saving
        return get_date_details(date_str)

    # --- Save Notes to YYYY-MM-DD_notes.md ---
    notes_file_path = os.path.join("data", f"{date_str}_notes.md")
    try:
        with open(notes_file_path, 'w', encoding='utf-8') as f:
            f.write(notes)
    except OSError as e:
        print(f"Error saving notes for {date_str}: {e}")
        # TODO: Add user-facing error message
        return get_date_details(date_str) # Return current state on error

    # --- Return Updated View --- #
    # Re-render the details for the specific date after saving
    return get_date_details(date_str)

# Main entry point remains the same
if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs("tasks", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 