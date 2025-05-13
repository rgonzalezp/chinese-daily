from fasthtml.common import Html, Head, Body, Title, P, Div, Link, Style
from starlette.responses import HTMLResponse
from ..main import app # Import the main app instance
from .. import config

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
            padding: 8px; 
            box-sizing: border-box; 
            text-align: center;
            overflow: hidden; /* Important to prevent scrollbars in the small iframe */
            background-color: var(--bg-color); /* Use theme variable */
            color: var(--text-color); /* Use theme variable */
            height: 100vh; /* Attempt to fill iframe, might need adjustment */
            display: flex;
            flex-direction: column;
            justify-content: space-around; /* Distribute content a bit */
        }
        h1 { 
            font-size: 1.2em; /* Smaller for preview */
            margin: 0.2em 0;
            color: var(--heading-color);
        }
        p { 
            font-size: 0.8em; /* Smaller for preview */
            margin: 0.2em 0;
        }
        .preview-button {
            padding: 5px 10px;
            border-radius: 4px;
            background-color: var(--primary-color);
            color: var(--bg-color); /* Assuming primary color is dark enough for light text */
            border: 1px solid var(--primary-dark);
            font-size: 0.9em;
            display: inline-block; /* Make it look like a button */
            margin-top: 5px;
        }
        .color-swatch {
            width: 20px;
            height: 20px;
            border-radius: 3px;
            display: inline-block;
            margin: 2px;
            border: 1px solid var(--border-color);
        }
    """)

    # Simplified mock content using theme variables
    mock_content = Body(
        Div(
            P("Theme: ", theme_id.replace("theme-", "")),
            Div(
                Div(cls="color-swatch", style="background-color: var(--bg-color);"),
                Div(cls="color-swatch", style="background-color: var(--text-color);"),
                Div(cls="color-swatch", style="background-color: var(--primary-color);"),
                Div(cls="color-swatch", style="background-color: var(--accent-color);")
            ),
            Div("Sample Button", cls="preview-button"),
            style="transform: scale(0.9); transform-origin: top left;" # Slightly scale down content to fit
        )
    )

    # The full HTML document for the iframe
    # We also link to the main theme.css so variables are available,
    # and our persistence script will also apply the class to this html doc.
    preview_doc = Html(
        Head(
            Title(f"Preview: {theme_id}"),
            Link(rel='stylesheet', href='/static/css/theme.css'), # So CSS vars are defined
            preview_specific_style,
            # We also need the theme persistence script here, or ensure the theme_id is applied directly
            # Simplest for iframe: apply directly and let theme.css work.
            # The global persistence script in main.py will run in the parent,
            # for the iframe, we pass the theme_id directly.
        ),
        mock_content,
        # Apply the theme class directly to the HTML tag for this specific preview.
        # The global script in main.py handles the main page's theme.
        # The CSS in theme.css is html.theme-X, so this is correct.
        cls=theme_id 
    )
    
    # Convert the tuple returned by Html() into a proper HTML string
    # preview_doc is typically (Doctype_instance, FT_html_instance)
    html_string = "".join(str(part) for part in preview_doc)
    
    return preview_doc

# Ensure this new routes file is imported in app/main.py
# You will need to manually add `from .web import routes_preview # noqa: F401` to app/main.py 