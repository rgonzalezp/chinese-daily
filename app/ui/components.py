import datetime

# Assuming this file is in app/ui/, import config from app/config.py
# --- Make imports relative to app package --- #
from .. import config
# Import FastHTML components
from fasthtml.common import A, Button, Div, H3, Li, Ul, Span # Add Span if needed
# ------------------------------------------ #

# --- Sidebar Components --- #

def _create_sidebar_day_button(day_name: str):
    """Creates a single sidebar button for editing a day's tasks."""
    return Li(Button(day_name,
                     hx_get=f'/edit-tasks/{day_name.lower()}', 
                     hx_target=config.MAIN_CONTENT_ID, 
                     hx_swap=f'innerHTML swap:{config.SWAP_DELAY_MS}ms',
                     cls='sidebar-button',hx_push_url="true"
                    ))

def _generate_sidebar():
    """Generates the complete sidebar Div."""
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    # Use constant for days
    sidebar_links = [_create_sidebar_day_button(day) for day in config.DAYS_OF_WEEK]
    today_button = Div(A("Today's Details", href="#", cls="sidebar-today-button",
                       hx_get=f"/view-day/{today_str}",
                       hx_target=config.CONTENT_SWAP_ID, 
                       hx_swap=f"outerHTML swap:{config.SWAP_DELAY_MS}ms"
                      ),hx_push_url="true", cls="sidebar-today-container")
    sidebar = Div(
        today_button,
        H3("Week Tasks", cls="sidebar-title"),
        Ul(*sidebar_links, cls="sidebar-nav"),
        id="sidebar", cls="sidebar"
    )
    return sidebar

# --- Navigation Components --- #

def day_nav_button(label: str, target_date_str: str, target_id: str = config.CONTENT_SWAP_ID):
    """Creates a navigation button link for days/weeks."""
    return A(label, cls="day-nav-button",
             hx_get=f"/view-day/{target_date_str}",
             hx_target=target_id,
             hx_swap=f"outerHTML swap:{config.SWAP_DELAY_MS}ms",
             hx_push_url="true")

# Potentially add calendar button helpers here too 