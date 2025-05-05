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
        Script("""
            // Global variable to hold the current EasyMDE instance
            window.currentEasyMDE = null;

            function initializeEasyMDE() {
                var textarea = document.getElementById('notes-editor-textarea');
                console.log('textarea:', textarea);
                if (!textarea) {
                    console.log('Textarea #notes-editor-textarea not found. Cleaning up any existing editor.');
                    // If textarea is gone, ensure editor instance is cleared
                    if (window.currentEasyMDE) {
                         window.currentEasyMDE = null;
                    }
                    // Also aggressively remove any visual container that might remain
                    var lingeringContainer = document.querySelector('.EasyMDEContainer');
                    if (lingeringContainer) {
                        console.log('Forcefully removing lingering .EasyMDEContainer.');
                        lingeringContainer.remove();
                    }
                    return; 
                }
                console.log('Found textarea:', textarea.id, 'Disabled:', textarea.disabled);

                // Check if a valid instance exists and its element is still in the DOM
                var editorExists = false;
                if (window.currentEasyMDE) {
                    try {
                        // Check if the CodeMirror wrapper element is still connected
                        if (window.currentEasyMDE.codemirror && window.currentEasyMDE.codemirror.getWrapperElement().isConnected) {
                            editorExists = true;
                        }
                    } catch (e) {
                         console.warn("Error checking existing EasyMDE instance:", e);
                         window.currentEasyMDE = null; // Invalidate potentially broken instance
                    }
                }

                if (editorExists) {
                    // --- Update Existing Instance --- 
                    console.log('Updating existing EasyMDE instance.');
                    // Update value from the (potentially new) textarea content
                    window.currentEasyMDE.value(textarea.value);
                    
                    // Update read-only state based on the textarea's disabled property
                    var isReadOnly = textarea.disabled;
                    window.currentEasyMDE.codemirror.setOption("readOnly", isReadOnly);
                    
                    // Optional: Add/remove a class to the wrapper for visual styling of disabled state?
                    var editorWrapper = window.currentEasyMDE.codemirror.getWrapperElement();
                    if(isReadOnly) {
                        editorWrapper.classList.add('editor-disabled');
                    } else {
                        editorWrapper.classList.remove('editor-disabled');
                    }

                } else {
                    // --- Create New Instance --- 
                    console.log('No valid existing EasyMDE instance found. Creating new one.');
                    
                    // Explicitly remove any lingering visual editor elements first
                    var existingContainer = document.querySelector('.EasyMDEContainer');
                    if (existingContainer) {
                        console.log("Removing lingering .EasyMDEContainer before creating new instance.");
                        existingContainer.remove();
                    }
                    window.currentEasyMDE = null; // Ensure it's null before creating
                    
                    // Initialize only if textarea is present and *not* disabled
                    if (!textarea.disabled) {
                        try {
                            console.log("--> Attempting to create NEW EasyMDE instance now...");
               // Configurations for easyMDE are applied HERE***************************************
                            var easyMDE = new EasyMDE({
                                element: textarea,
                                spellChecker: true,
                                status: false,
                                lineWrapping: true,
                                onToggleFullScreen: function(fullscreen) {
                                    if (fullscreen) {
                                        requestAnimationFrame(() => {
                                            document.documentElement.style.overflow = 'auto';
                                            document.body.style.overflow = 'auto';
                                        });
                                    } else {
                                        document.documentElement.style.overflow = '';
                                        document.body.style.overflow = '';
                                    }
                                }
                            });
                            // Store the new instance globally
                            window.currentEasyMDE = easyMDE;
                            
                            easyMDE.codemirror.on('change', function() { easyMDE.codemirror.save(); });
                            console.log("New EasyMDE Initialized successfully.");
                        } catch (e) {
                            console.error("EasyMDE Init Error:", e);
                            window.currentEasyMDE = null; // Ensure it's null on error
                            // Attempt cleanup
                            var failedContainer = textarea.parentNode?.querySelector('.EasyMDEContainer');
                            if(failedContainer) failedContainer.remove();
                        }
                    } else {
                        console.log('Textarea is disabled, skipping new EasyMDE creation.');
                         window.currentEasyMDE = null; // Ensure no instance is stored
                    }
                }
            }

            // Run on initial load and potentially after HTMX swaps (via hx-on::load)
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