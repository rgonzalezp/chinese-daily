from fasthtml.common import Div, H1, H2, P, Title, A, Main, Section, Header, Style, Script, Iframe, Button
from starlette.requests import Request # Added Request
from starlette.responses import HTMLResponse # Added HTMLResponse
from .. import config
from ..main import app # Import the main app instance
from ..ui.components import _generate_breadcrumbs, _generate_sidebar # ADDED _generate_sidebar

# Potentially import other components or services as the page develops
# from ..ui.components import some_component

# Helper to create a theme item for the grid
def _create_theme_item(theme_name: str, theme_description: str, theme_id: str):
    """Creates a clickable grid item for a theme."""
    preview_iframe = Iframe(
        src=f"/?preview_theme={theme_id}", # Set initial src with theme
        loading="lazy", # Defer loading until near viewport
        # title=f"Interactive preview of {theme_name} theme", # Good for accessibility
        # scrolling="no", # Prevent scrollbars inside iframe if content fits
        # sandbox="allow-scripts allow-same-origin", # For security if needed
        cls="theme-preview-iframe" # Class for styling
    )

    preview_iframe.attrs["id"] = f"iframe-{theme_id}"

    expand_button = Button(
        "[Preview]", 
        cls="expand-preview-btn", 
        data_iframe_id=f"iframe-{theme_id}",
        data_theme_id=theme_id # Add the actual theme_id here
    )

    apply_theme_button = Button(
        "Apply Theme",
        cls="apply-theme-btn", # Add a class for styling if needed
        hx_post=f"/apply-theme/{theme_id}",
        hx_target="body",
        hx_swap="beforeend",
        # hx_indicator="#loading-indicator" # Optional: if you have a global loading indicator
    )

    return Div( # Was A()
        Div(
            H2(theme_name, cls="theme-item-title"),
            P(theme_description, cls="theme-item-description"),
            Div(
                preview_iframe, 
                expand_button, 
                cls="theme-preview-container"
            ),
            apply_theme_button, # Add the new apply button here
            cls="theme-item-content"
        ),
        # Removed href, hx_post, hx_target, hx_swap from here
        cls="theme-grid-item" # This class styles the card itself
    )

@app.route("/personalize")
def get_personalize_page(request: Request): # Added request: Request
    """Serves the main personalize page with a grid of themes."""
    
    # Use theme IDs that match CSS classes (prefixed with 'theme-')
    # Define the "Red Sun" theme ID
    default_theme_id = "theme-red-sun" # Explicit ID for the default

    theme_items = [
        _create_theme_item("Red Sun", "The standard light theme.", default_theme_id), 
        _create_theme_item("Boba", "Creamy yellows and pastel browns.", "theme-boba"), 
        _create_theme_item("Midnight Dark", "A sleek dark mode experience.", "theme-midnight-dark"),
        _create_theme_item("Ocean Blue", "Cool and calming blue tones.", "theme-ocean-blue"),
        _create_theme_item("Forest Green", "Earthy and natural greens.", "theme-forest-green"),

    ]
    
    theme_grid = Div(*theme_items, cls="theme-grid")
    
    breadcrumbs = _generate_breadcrumbs([
        ("Home", "/"),
        ("Personalize", None) # Current page
    ])

    page_content_inner = Main( 
        breadcrumbs,
        Header(H1("Personalize Your Experience", cls="page-title"), cls="page-header"),
        Section(
            P("Choose a theme below to change the application's appearance.", cls="page-description"),
            theme_grid,
            cls="personalize-options"
        ),
        id="personalize-page-content" # Ensure a unique ID, and no cls="main-content-area"
    )
    
    linked_css = Style("", src="/static/css/personalize.css")
    linked_js = Script(src="/static/js/personalize_interactions.js") # Added JS link
    page_title = Title("Personalize")

    if "hx-request" not in request.headers:
        # Full page request: include sidebar and full layout
        sidebar = _generate_sidebar()
        content_for_full_page = Div(page_content_inner, id="content-swap-wrapper", cls="page-content-entry") 
        full_page_main_content = Div(content_for_full_page, id=config.MAIN_CONTENT_ID.strip('#'), cls="main-content")
        # Include linked_js for full page loads
        return page_title, linked_css, linked_js, Div(Div(sidebar, full_page_main_content, cls="layout-container"))
    else:
        # HTMX request: return title, CSS, and the inner content wrapped in #content-swap-wrapper
        # JS for modal is already on the page from full load, so no need to re-send unless it was part of the swap
        htmx_response_content = Div(page_content_inner, id="content-swap-wrapper", cls="page-content-entry")
        # If the modal JS needed to be re-initialized on HTMX swap, we might include linked_js here too,
        # or ensure the script handles dynamic content if expand buttons are swapped in.
        # For now, assuming expand buttons are part of initial load of this component.
        return page_title, linked_css, htmx_response_content 

# New endpoint to apply the theme
@app.post("/apply-theme/{theme_id:str}")
async def apply_theme(theme_id: str):
    """Applies the selected theme by returning Script components to be appended to the body."""
    
    if not theme_id or not theme_id.startswith("theme-"):
        # Return nothing or an empty tuple if validation fails, 
        # or a specific error component if you want to show an error.
        return ()

    return (
        Script(f"window.themeToApply = '{theme_id}';"),
        Script(src='/static/js/apply_theme.js', defer=False)
    ) 