import datetime
import os
import uvicorn
from fasthtml.common import FastHTML, Link, Script, Head, Meta
from starlette.staticfiles import StaticFiles

# Assuming config lives alongside main.py in the 'app' directory
from . import config

# Define the main FastHTML app instance
# Shared across route modules
app = FastHTML(
    hdrs=[
        Link(rel='stylesheet', href='/static/css/main.css'),
        Link(rel='stylesheet', href='https://unpkg.com/easymde/dist/easymde.min.css'),
        Script(src='https://unpkg.com/easymde/dist/easymde.min.js'),
        Script(src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.4/dist/htmx.min.js"),

        # Add our custom global script for EasyMDE initialization
        Script(src='/static/js/mde_injection.js'),
        # Add our new sidebar interactions script
        Script(src='/static/js/sidebar_interactions.js'),

        # Script to apply saved theme on page load
        Script("""
(function() {
    const savedTheme = localStorage.getItem('selectedTheme');
    const defaultTheme = 'theme-red-sun'; // Default theme class
    const themeToApply = savedTheme || defaultTheme;
    // Apply class to HTML element as body might not exist yet
    document.documentElement.className = document.documentElement.className.replace(/theme-\S+/g, '').trim(); // Clear existing and trim whitespace
    if (themeToApply) {
        document.documentElement.classList.add(themeToApply);
    }
})();
        """)
    ]
)

# Mount static files directory (using path from config)
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# --- Import route modules to register their routes --- #
# Use try-except for potentially cleaner handling if module not found?
# For now, direct imports. Ensure these files exist in app/web/
# The noqa comment prevents linters from complaining about unused imports,
# as their side effect (route registration) is the purpose.
from .web import routes_notes    # noqa: F401
from .web import routes_calendar  # noqa: F401
from .web import routes_tasks     # noqa: F401
from .web import routes_personalize # noqa: F401
# ---------------------------------------------------- #

# Import UI components and other necessary modules
from .ui.components import _generate_sidebar

if __name__ == "__main__":
    # Create necessary directories if they don't exist (using config)
    config.TASKS_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run the Uvicorn server
    # Note: Uvicorn needs the import string "app.main:app" if run from project root
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(config.BASE_DIR / 'app')]) 