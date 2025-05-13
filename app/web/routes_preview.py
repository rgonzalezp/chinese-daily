from fasthtml.common import Html, Head, Body, Title, P, Div, Link, Style, Table, Thead, Tbody, Tr, Th, Td, Span
from starlette.responses import HTMLResponse
from ..main import app # Import the main app instance
from .. import config
from ..services import calendar as calendar_service
import datetime

# Helper function to generate a simplified calendar for preview
def _generate_simplified_calendar_preview(year, month):
    cal_matrix = calendar_service.month_matrix(year, month)
    today = datetime.date.today() # For styling 'today'

    # Calendar Table Generation (simplified)
    header_row = Tr(*[Th(day_name, style="padding: 2px; font-size: 0.7em;") for day_name in config.SHORT_DAYS], cls='calendar-header')
    weeks_trs = []
    for week in cal_matrix:
        day_tds = []
        for day_num in week:
            cell_cls = "calendar-cell"
            day_content_children = []
            cell_style = "padding: 3px; height: 25px; width: 25px; text-align: center; font-size: 0.65em;"

            if day_num == 0:
                cell_cls += " empty"
                day_tds.append(Td(style=cell_style, cls=cell_cls))
            else:
                current_date = datetime.date(year, month, day_num)
                cell_cls += " active"
                if current_date == today:
                    cell_cls += " today"
                day_content_children = [Span(str(day_num), cls='day-number')]
                day_tds.append(Td(*day_content_children, style=cell_style, cls=cell_cls))
        weeks_trs.append(Tr(*day_tds))

    calendar_table = Table(Thead(header_row), Tbody(*weeks_trs), cls='calendar-grid', style="width: 100%; border-collapse: collapse;")
    
    # Add a small title above the calendar
    month_name = datetime.date(year, month, 1).strftime("%B %Y")
    preview_title = P(f"{month_name} Preview", style="font-size: 0.9em; margin-bottom: 5px; color: var(--heading-color);");

    return Div(preview_title, calendar_table, style="transform: scale(1.0); transform-origin: top center;") # Scale down slightly more

@app.route("/render-preview/{theme_id:str}")
async def render_theme_preview(theme_id: str):
    """
    Renders a simplified view of the application with a specific theme applied.
    This content is intended to be displayed within an iframe on the personalize page.
    """

    # Basic validation for theme_id (optional, but good practice)
    if not theme_id or not theme_id.startswith("theme-"):
        return HTMLResponse("Invalid theme ID", status_code=400)

    # Construct the HTML for the preview
    # Important: The <html> tag gets the theme_id class
    
    # Minimal CSS for the preview itself to ensure it's somewhat presentable
    # and to override any global styles that might interfere in a tiny iframe.
    preview_specific_style = Style("""
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 5px; /* Reduced padding */
            box-sizing: border-box; 
            text-align: center;
            overflow: hidden; /* Important to prevent scrollbars in the small iframe */
            background-color: var(--bg-color); /* Use theme variable */
            color: var(--text-color); /* Use theme variable */
            height: 100vh; /* Attempt to fill iframe */
            display: flex;
            flex-direction: column;
            align-items: center; /* Center content like the calendar */
            justify-content: center; /* Center content vertically */
        }
        /* Remove specific h1, p, button, swatch styles as calendar is the main content */
        /* Styles for calendar cells will be inherited from theme.css or inline */
        .calendar-cell.today {
            /* Ensure today is highlighted, might need !important if theme.css overrides too strongly */
            /* For preview, simple border or background might be enough */
            /* Preview specific 'today' style can go here if needed */
        }
        .calendar-cell.active {
            /* Preview specific 'active' style can go here if needed */
        }
    """)

    # Generate simplified calendar content for a fixed or current month
    # For example, always show January of the current year for consistency in previews
    current_year = datetime.datetime.now().year
    # preview_month = 1 # January
    preview_month = datetime.datetime.now().month # Or current month for relevance

    simplified_calendar_content = _generate_simplified_calendar_preview(current_year, preview_month)

    # Replace mock_content with the simplified calendar
    # The Body will now contain our simplified calendar
    themed_body_content = Body(
        simplified_calendar_content
        # Div(
        #     P("Theme: ", theme_id.replace("theme-", "")),
        #     Div(
        #         Div(cls="color-swatch", style="background-color: var(--bg-color);"),
        #         Div(cls="color-swatch", style="background-color: var(--text-color);"),
        #         Div(cls="color-swatch", style="background-color: var(--primary-color);"),
        #         Div(cls="color-swatch", style="background-color: var(--accent-color);")
        #     ),
        #     Div("Sample Button", cls="preview-button"),
        #     style="transform: scale(0.9); transform-origin: top left;" # Slightly scale down content to fit
        # )
    )

    # The full HTML document for the iframe
    # We also link to the main theme.css so variables are available,
    # and our persistence script will also apply the class to this html doc.
    preview_doc = Html(
        Head(
            Title(f"Preview: {theme_id}"),
            Link(rel='stylesheet', href='/static/css/theme.css'), # So CSS vars are defined
            Link(rel='stylesheet', href='/static/css/main.css'), # To get calendar styles like .calendar-cell, .today
            preview_specific_style,
            # We also need the theme persistence script here, or ensure the theme_id is applied directly
            # Simplest for iframe: apply directly and let theme.css work.
            # The global persistence script in main.py will run in the parent,
            # for the iframe, we pass the theme_id directly.
        ),
        themed_body_content,
        # Apply the theme class directly to the HTML tag for this specific preview.
        # The global script in main.py handles the main page's theme.
        # The CSS in theme.css is html.theme-X, so this is correct.
        cls=theme_id 
    )
    

    
    return preview_doc

# Ensure this new routes file is imported in app/main.py
# You will need to manually add `from .web import routes_preview # noqa: F401` to app/main.py 