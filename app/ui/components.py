import datetime

# Assuming this file is in app/ui/, import config from app/config.py
# --- Make imports relative to app package --- #
from .. import config
# Import FastHTML components
from fasthtml.common import A, Button, Div, H3, Li, Ul, Span, Nav # Add Span if needed
# ------------------------------------------ #

# --- Sidebar Components --- #

def _create_sidebar_day_button(day_name: str):
    """Creates a single sidebar button for editing a day's tasks."""
    return Li(Button(day_name,
                     hx_get=f'/edit-tasks/{day_name.lower()}', 
                     hx_target=config.MAIN_CONTENT_ID, 
                     hx_swap=f'innerHTML swap:{config.SWAP_DELAY_MS}ms',
                     cls='sidebar-button weekday-button',hx_push_url="true"
                    ))

def _generate_sidebar():
    """Generates the complete sidebar Div."""
    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    
    sidebar_day_links = [_create_sidebar_day_button(day) for day in config.DAYS_OF_WEEK]
    
    today_button = Div(A("Today's Details", href="#", cls="sidebar-today-button",
                       hx_get=f"/view-day/{today_str}",
                       hx_target=config.MAIN_CONTENT_ID,
                       hx_swap=f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
                       hx_push_url="true"
                      ), cls="sidebar-today-container")

    templates_button_container = Div(
        Button("Templates", cls="sidebar-button templates-dropdown-button"),
        Ul(*sidebar_day_links, cls="sidebar-nav weekday-links-list"),
        cls="templates-container"
    )
    
    personalize_button = Div(Button("Personalize",
                                  cls="sidebar-button personalize-button",
                                  hx_get="/personalize", 
                                  hx_target=config.MAIN_CONTENT_ID,
                                  hx_swap=f'innerHTML swap:{config.SWAP_DELAY_MS}ms',
                                  hx_push_url="true"
                                 ),
                         cls="personalize-button-container")

    sidebar = Div(
        today_button,
        H3("Actions", cls="sidebar-title"),
        personalize_button,
        templates_button_container,
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

# --- Breadcrumb Component --- #
def _generate_breadcrumbs(crumbs: list[tuple[str, str | None]]):
    """Generates breadcrumb navigation HTML.
    Each crumb in the list is a tuple: (label, hx_get_url_or_None_if_current).
    The last item is treated as the current page if its URL is None.
    """
    if not crumbs:
        return ""

    li_items = []
    for i, (label, url) in enumerate(crumbs):
        if url and (i < len(crumbs) - 1 or crumbs[-1][1] is not None): # It's a link and not the last item if last item is not a link
            # Link item
            li_items.append(
                Li(A(label, 
                     href="#", # href="#" or actual URL if not HTMX only
                     hx_get=url, 
                     hx_target=config.MAIN_CONTENT_ID,
                     hx_swap=f"innerHTML swap:{config.SWAP_DELAY_MS}ms",
                     hx_push_url="true"
                    ),
                   cls="breadcrumb-item")
            )
        else:
            # Current page (not a link) or last item is current
            li_items.append(Li(label, cls="breadcrumb-item active", aria_current="page"))

    return Nav(Ul(*li_items, cls="breadcrumb"), aria_label="breadcrumb", cls="breadcrumb-nav-container") 