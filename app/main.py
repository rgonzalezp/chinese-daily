import datetime
import os
import uvicorn
from fasthtml.common import FastHTML, Link, Script
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
        Script(src="https://unpkg.com/htmx.org@2.0.1/dist/htmx.min.js"),
        # Add our custom global script for EasyMDE initialization
        Script("""
            function initializeEasyMDE() {
                var textarea = document.getElementById('notes-editor-textarea');
                if (!textarea) {
                    // console.log('Textarea #notes-editor-textarea not found, skipping EasyMDE init.');
                    return; // Exit if no textarea
                }
                console.log('Attempting EasyMDE init for:', textarea.id);
                
                // Clean up previous instance if it exists
                var parent = textarea.parentNode;
                var existingEditor = parent ? parent.querySelector('.EasyMDEContainer') : null;
                if (existingEditor) {
                    console.log("Removing existing EasyMDE container before re-init.");
                    existingEditor.remove();
                    textarea.classList.remove('easymde-initialized'); 
                }

                // Initialize only if textarea is present, enabled, and not already marked
                if (!textarea.disabled && !textarea.classList.contains('easymde-initialized')) {
                    try {
                        console.log("Initializing EasyMDE...");
                        var easyMDE = new EasyMDE({
                            element: textarea, 
                            spellChecker: false, 
                            status: false,
                            lineWrapping: true
                        });
                        textarea.classList.add('easymde-initialized');
                        easyMDE.codemirror.on('change', function() { easyMDE.codemirror.save(); });
                        console.log("EasyMDE Initialized successfully.");
                    } catch (e) {
                        console.error("EasyMDE Init Error:", e);
                        textarea.classList.remove('easymde-initialized'); // Clean up flag on error
                    }
                } else if (textarea.disabled) {
                    console.log('Textarea is disabled, skipping EasyMDE init.');
                } else if (textarea.classList.contains('easymde-initialized')) {
                    console.log('Textarea already marked as initialized, skipping EasyMDE init.');
                }
            }

            // Run on initial load
            document.addEventListener('DOMContentLoaded', initializeEasyMDE);
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
from .web import routes_calendar # noqa: F401
from .web import routes_tasks    # noqa: F401
from .web import routes_notes    # noqa: F401
# ---------------------------------------------------- #

if __name__ == "__main__":
    # Create necessary directories if they don't exist (using config)
    config.TASKS_DIR.mkdir(parents=True, exist_ok=True)
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run the Uvicorn server
    # Note: Uvicorn needs the import string "app.main:app" if run from project root
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(config.BASE_DIR / 'app')]) 