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
                                    // Ensure we have the editor instance
                                    if (!easyMDE || !easyMDE.codemirror) {
                                        console.error("EasyMDE instance not available for fullscreen toggle.");
                                        return;
                                    }
                                    const editorWrapper = easyMDE.codemirror.getWrapperElement();
                                    const duration = 550; // Animation duration in ms

                                    // --- Handle scroll restoration and body overflow ---
                                    const originalBodyOverflow = document.body.style.overflow;
                                    const originalDocElementOverflow = document.documentElement.style.overflow;
                                    
                                    if (fullscreen) {
                                        // Entering fullscreen: Set overflow (saving scroll position removed)
                                        document.documentElement.style.overflow = 'auto'; // Keep user's change
                                        document.body.style.overflow = 'auto';      // Keep user's change
                                    } else {
                                        // Exiting fullscreen: Set overflow (restoring scroll removed)
                                        document.documentElement.style.overflow = 'auto';
                                        document.body.style.overflow = 'auto';
                                    }

                                    // Get the initial bounding rectangle
                                    const initialRect = editorWrapper.getBoundingClientRect();
                                    editorWrapper.style.transition = 'none'; // Disable transitions during setup

                                    // Use rAF to ensure calculations happen after potential EasyMDE style applications/removals
                                    requestAnimationFrame(() => {
                                        // Get the final bounding rectangle (after EasyMDE changes)
                                        const finalRect = editorWrapper.getBoundingClientRect();

                                        // Calculate the necessary transform to make the final state look like the initial state
                                        const scaleX = finalRect.width ? initialRect.width / finalRect.width : 1;
                                        const scaleY = finalRect.height ? initialRect.height / finalRect.height : 1;
                                        const translateX = initialRect.left - finalRect.left;
                                        const translateY = initialRect.top - finalRect.top;

                                        // Apply the inverse transform immediately, only if necessary
                                        // (Avoid applying identity transform if rects are somehow identical)
                                        if (translateX !== 0 || translateY !== 0 || scaleX !== 1 || scaleY !== 1) {
                                            editorWrapper.style.transformOrigin = 'top left';
                                            editorWrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scaleX}, ${scaleY})`;
                                        } else {
                                            // No visual change needed, skip transform
                                        }


                                        // Force reflow to apply the transform before adding the transition
                                        editorWrapper.offsetHeight;

                                        // Add the transition effect for the transform property
                                        editorWrapper.style.transition = `transform ${duration}ms ease-in-out`;

                                        // Reset transform to trigger the animation to the actual final state
                                        editorWrapper.style.transform = 'translate(0, 0) scale(1, 1)'; // Or 'none' could work

                                        // --- Smooth Scroll --- 
                                        if (fullscreen) {
                                            // Scroll to top smoothly AFTER starting the FLIP animation
                                            window.scrollTo({ top: 0, behavior: 'smooth' });
                                        } // Scroll back happens in setTimeout

                                        // Clean up after animation completes
                                        setTimeout(() => {
                                            editorWrapper.style.transition = '';
                                            editorWrapper.style.transformOrigin = '';
                                            editorWrapper.style.transform = ''; // Clear transform style explicitly

                                            // --- Final Scroll & Overflow State ---
                                            if (fullscreen) {
                                                // In fullscreen: ensure overflow is auto (user's preference)
                                                document.documentElement.style.overflow = 'auto'; 
                                                document.body.style.overflow = 'auto';
                                            } else {
                                                // Exiting fullscreen: Restore previous overflow (scroll restoration removed)
                                                document.documentElement.style.overflow = originalDocElementOverflow;
                                                document.body.style.overflow = originalBodyOverflow;
                                            }
                                        }, duration);
                                    });
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