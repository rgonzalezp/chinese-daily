import datetime
import calendar
from starlette.requests import Request

# Assuming this file is in app/web/, import app from app/main.py
# --- Make imports relative to app package --- #
from ..main import app 
from .. import config
from ..ui.components import _generate_sidebar
from ..services import calendar as calendar_service
from fasthtml.common import A, Div, Span, Table, Tbody, Td, Th, Thead, Tr, Title, H1, Script
# ------------------------------------------ #

# Updated Helper function to generate the calendar HTML + Controls
# TODO: Consider moving this to services/calendar.py or ui/components.py
def generate_calendar(year, month):
    # Use calendar service for matrix
    cal = calendar_service.month_matrix(year, month)
    today = datetime.date.today()
    current_dt = datetime.date(year, month, 1)
    
    # --- Use Calendar Service for adjacent months --- 
    prev_year, prev_month = calendar_service.adjacent_month(year, month, -1)
    next_year, next_month = calendar_service.adjacent_month(year, month, 1)
    # ------------------------------------------------ #
    
    swap_outer_html = f"outerHTML swap:{config.SWAP_DELAY_MS}ms"

    # Controls
    controls = Div(
        A("< Prev", href=f"/?year={prev_year}&month={prev_month}", cls="cal-nav",
          hx_get=f"/?year={prev_year}&month={prev_month}", 
          hx_target=config.MAIN_CONTENT_ID,
          hx_swap=f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
          hx_push_url="true"),
        Span(f"{current_dt.strftime('%B %Y')}", cls="cal-month-year"),
        A("Next >", href=f"/?year={next_year}&month={next_month}", cls="cal-nav",
          hx_get=f"/?year={next_year}&month={next_month}", 
          hx_target=config.MAIN_CONTENT_ID,
          hx_swap=f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
          hx_push_url="true"),
        cls="calendar-controls"
    )

    # Calendar Table Generation
    header_row = Tr(*[Th(day) for day in config.SHORT_DAYS], cls='calendar-header')
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
                    'hx_get': f'/view-day/{date_str}',
                    'hx_target': config.MAIN_CONTENT_ID,
                    'hx_swap': f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
                    'hx-push-url': f'/view-day/{date_str}'
                }
            row.append(Td(*day_content_children, cls=cell_cls, **htmx_attrs))
        weeks.append(Tr(*row))

    calendar_table = Table(Thead(header_row), Tbody(*weeks), cls='calendar-grid')

    # Return controls and table WRAPPED in the swappable div
    return Div(controls, calendar_table, 
               id=config.CONTENT_SWAP_ID.strip('#'), # Use ID without #
               cls="page-content-entry" # ADDED CLASS for entry animation
              )

# Root route - handles optional year/month for calendar display
@app.get("/")
def home(request: Request):
    try:
        year = int(request.query_params.get("year", datetime.datetime.now().year))
        month = int(request.query_params.get("month", datetime.datetime.now().month))
        if not (1 <= month <= 12):
             month = datetime.datetime.now().month
             year = datetime.datetime.now().year
    except ValueError:
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month

    # Generate Calendar View - it returns the #content-swap-wrapper div
    calendar_content = generate_calendar(year, month)

    # --- Theme forcing for iframe preview --- 
    preview_theme_script = None
    preview_theme_val = request.query_params.get("preview_theme")
    if preview_theme_val and preview_theme_val.startswith("theme-"):
        # Make sure the theme name is safe to inject if necessary (though here it's just class name)
        # This script runs immediately in the body of the iframe.
        # It attempts to override any theme set by the main persistence script.
        script_content = f"""
(function() {{
    const themeToForce = '{preview_theme_val}';
    console.log('[iframe-preview] Forcing theme:', themeToForce);
    const rootEl = document.documentElement;
    rootEl.className = rootEl.className.replace(/theme-\S+/g, '').trim();
    rootEl.classList.add(themeToForce);
    // We could also try to override localStorage for selectedTheme temporarily,
    // but that might have side effects if the user navigates away from the iframe.
    // For now, just class override is safest for visual preview.
}})();
        """
        preview_theme_script = Script(script_content)
    # -------------------------------------- #

    # For full page load, wrap it in the main layout
    if "hx-request" not in request.headers:
        sidebar = _generate_sidebar() 
        main_content_children = [calendar_content]
        if preview_theme_script:
            # Prepend script so it runs early in the body of the iframe
            main_content_children.insert(0, preview_theme_script)
        
        main_content_div = Div(*main_content_children, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
        
        # The Title component is usually separate and handled by FastHTML before body components
        return Title("Weekly Task Notes"), Div(sidebar, main_content_div, cls="layout-container")
    else:
        # For HTMX requests (like prev/next month), just return the calendar part
        # If it's an HTMX swap within the preview iframe, this script also needs to be there.
        if preview_theme_script:
            return preview_theme_script, calendar_content # Return script then content
        else:
            return calendar_content 