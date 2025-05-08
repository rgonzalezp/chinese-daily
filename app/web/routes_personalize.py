from fasthtml.common import Div, H1, H2, P, Title, A, Main, Section, Header, Style
from starlette.requests import Request # Added Request
from .. import config
from ..main import app # Import the main app instance
from ..ui.components import _generate_breadcrumbs, _generate_sidebar # ADDED _generate_sidebar

# Potentially import other components or services as the page develops
# from ..ui.components import some_component

# Helper to create a theme item for the grid
def _create_theme_item(theme_name: str, theme_description: str, theme_id: str):
    """Creates a clickable grid item for a theme."""
    return A( # Make the whole item clickable
        Div(
            H2(theme_name, cls="theme-item-title"),
            P(theme_description, cls="theme-item-description"),
            cls="theme-item-content"
        ),
        href=f"/apply-theme/{theme_id}", # Example action
        hx_post=f"/apply-theme/{theme_id}", # Example HTMX action
        hx_target="#main-content", # Or body, or a specific element for feedback
        hx_swap="innerHTML", # Or an appropriate swap
        cls="theme-grid-item"
    )

@app.route("/personalize")
def get_personalize_page(request: Request): # Added request: Request
    """Serves the main personalize page with a grid of themes."""
    
    # Example theme items
    theme_items = [
        _create_theme_item("Default Light", "The standard light and airy theme.", "default-light"),
        _create_theme_item("Midnight Dark", "A sleek dark mode experience.", "midnight-dark"),
        _create_theme_item("Ocean Blue", "Cool and calming blue tones.", "ocean-blue"),
        _create_theme_item("Forest Green", "Earthy and natural greens.", "forest-green"),
        # Add more themes as needed
    ]
    
    theme_grid = Div(*theme_items, cls="theme-grid")
    
    breadcrumbs = _generate_breadcrumbs([
        ("Home", "/"),
        ("Personalize", None) # Current page
    ])

    page_content_inner = Main( # Renamed to page_content_inner
        breadcrumbs,
        Header(H1("Personalize Your Experience", cls="page-title"), cls="page-header"),
        Section(
            P("Choose a theme below to change the application's appearance.", cls="page-description"),
            theme_grid,
            cls="personalize-options"
        ),
        id="personalize-content-area", # Changed ID slightly to avoid conflict if MAIN_CONTENT_ID is this ID.
        cls="main-content-area"
    )
    
    linked_css = Style("", src="/static/css/personalize.css")
    page_title = Title("Personalize")

    if "hx-request" not in request.headers:
        # Full page request: include sidebar and full layout
        sidebar = _generate_sidebar()
        # Wrap the page_content_inner in the main content container for full page loads.
        # The ID MAIN_CONTENT_ID is applied to this outer Div for full page context.
        full_page_main_content = Div(page_content_inner, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
        return page_title, linked_css, Div(Div(sidebar, full_page_main_content, cls="layout-container"))
    else:
        # HTMX request: return only the title, CSS, and the inner content for swapping
        return page_title, linked_css, page_content_inner 