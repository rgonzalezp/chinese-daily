// Global variable to hold the current EasyMDE instance
window.currentEasyMDE = null;
window.currentTasksMDE = null; // Added for the tasks MDE

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

// Function to initialize the Tasks EasyMDE instance
function initializeTasksMDE() {
    var textarea = document.getElementById('tasks-editor-textarea'); // New ID for tasks editor
    console.log('Tasks MDE - textarea:', textarea);
    if (!textarea) {
        console.log('Tasks MDE - Textarea #tasks-editor-textarea not found. Cleaning up any existing editor.');
        if (window.currentTasksMDE) {
             window.currentTasksMDE = null;
        }
        var lingeringContainer = document.querySelector('#tasks-editor-textarea + .EasyMDEContainer'); // More specific selector
        if (lingeringContainer) {
            console.log('Tasks MDE - Forcefully removing lingering .EasyMDEContainer for tasks.');
            lingeringContainer.remove();
        }
        return; 
    }
    console.log('Tasks MDE - Found textarea:', textarea.id, 'Disabled:', textarea.disabled);

    var editorExists = false;
    if (window.currentTasksMDE) {
        try {
            if (window.currentTasksMDE.codemirror && window.currentTasksMDE.codemirror.getWrapperElement().isConnected) {
                editorExists = true;
            }
        } catch (e) {
             console.warn("Tasks MDE - Error checking existing EasyMDE instance:", e);
             window.currentTasksMDE = null;
        }
    }

    if (editorExists) {
        console.log('Tasks MDE - Updating existing EasyMDE instance.');
        window.currentTasksMDE.value(textarea.value);
        
        var isReadOnly = textarea.disabled;
        window.currentTasksMDE.codemirror.setOption("readOnly", isReadOnly);
        
        var editorWrapper = window.currentTasksMDE.codemirror.getWrapperElement();
        if(isReadOnly) {
            editorWrapper.classList.add('editor-disabled');
        } else {
            editorWrapper.classList.remove('editor-disabled');
        }

    } else {
        console.log('Tasks MDE - No valid existing EasyMDE instance found. Creating new one.');
        
        var existingContainer = document.querySelector('#tasks-editor-textarea + .EasyMDEContainer'); // More specific selector
        if (existingContainer) {
            console.log("Tasks MDE - Removing lingering .EasyMDEContainer before creating new instance.");
            existingContainer.remove();
        }
        window.currentTasksMDE = null;
        
        if (!textarea.disabled) {
            try {
                console.log("Tasks MDE - --> Attempting to create NEW EasyMDE instance now...");
                var tasksMDE = new EasyMDE({ // Changed variable name for clarity
                    element: textarea,
                    spellChecker: true,
                    status: false,
                    lineWrapping: true,
                    // For now, keep the same onToggleFullScreen logic. This could be refactored later if needed.
                    onToggleFullScreen: function(fullscreen) {
                        if (!tasksMDE || !tasksMDE.codemirror) { // Use tasksMDE here
                            console.error("Tasks MDE - EasyMDE instance not available for fullscreen toggle.");
                            return;
                        }
                        const editorWrapper = tasksMDE.codemirror.getWrapperElement(); // Use tasksMDE here
                        const duration = 550; 

                        const originalBodyOverflow = document.body.style.overflow;
                        const originalDocElementOverflow = document.documentElement.style.overflow;
                        
                        if (fullscreen) {
                            document.documentElement.style.overflow = 'auto'; 
                            document.body.style.overflow = 'auto';      
                        } else {
                            document.documentElement.style.overflow = 'auto';
                            document.body.style.overflow = 'auto';
                        }

                        const initialRect = editorWrapper.getBoundingClientRect();
                        editorWrapper.style.transition = 'none'; 

                        requestAnimationFrame(() => {
                            const finalRect = editorWrapper.getBoundingClientRect();
                            const scaleX = finalRect.width ? initialRect.width / finalRect.width : 1;
                            const scaleY = finalRect.height ? initialRect.height / finalRect.height : 1;
                            const translateX = initialRect.left - finalRect.left;
                            const translateY = initialRect.top - finalRect.top;

                            if (translateX !== 0 || translateY !== 0 || scaleX !== 1 || scaleY !== 1) {
                                editorWrapper.style.transformOrigin = 'top left';
                                editorWrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scaleX}, ${scaleY})`;
                            }

                            editorWrapper.offsetHeight;
                            editorWrapper.style.transition = `transform ${duration}ms ease-in-out`;
                            editorWrapper.style.transform = 'translate(0, 0) scale(1, 1)';

                            if (fullscreen) {
                                window.scrollTo({ top: 0, behavior: 'smooth' });
                            } 

                            setTimeout(() => {
                                editorWrapper.style.transition = '';
                                editorWrapper.style.transformOrigin = '';
                                editorWrapper.style.transform = ''; 

                                if (fullscreen) {
                                    document.documentElement.style.overflow = 'auto'; 
                                    document.body.style.overflow = 'auto';
                                } else {
                                    document.documentElement.style.overflow = originalDocElementOverflow;
                                    document.body.style.overflow = originalBodyOverflow;
                                }
                            }, duration);
                        });
                    }
                });
                window.currentTasksMDE = tasksMDE; // Store new instance
                
                tasksMDE.codemirror.on('change', function() { tasksMDE.codemirror.save(); });
                console.log("Tasks MDE - New EasyMDE Initialized successfully.");
            } catch (e) {
                console.error("Tasks MDE - EasyMDE Init Error:", e);
                window.currentTasksMDE = null; 
                var failedContainer = textarea.parentNode?.querySelector('.EasyMDEContainer'); // General selector for cleanup
                if(failedContainer) failedContainer.remove();
            }
        } else {
            console.log('Tasks MDE - Textarea is disabled, skipping new EasyMDE creation.');
             window.currentTasksMDE = null;
        }
    }
}

// Run on initial load and potentially after HTMX swaps (via hx-on::load)
document.addEventListener('DOMContentLoaded', initializeEasyMDE);

// --- FLIP Animation for Task Block Swapping --- //
htmx.onLoad(function(elt) {
    // Function to initialize FLIP listeners on a given task block
    function setupFlipForTaskBlock(taskBlock) {
        if (!taskBlock || taskBlock.dataset.flipListenersAttached === 'true') {
            return;
        }

        let firstRect = null;
        // Using a more specific flag or way to ensure context if needed for complex scenarios
        // For now, this assumes htmx:beforeSwap on taskBlock means it is the one being replaced
        // and htmx:afterSwap on taskBlock means it is the new content that replaced the old one.

        taskBlock.addEventListener('htmx:beforeSwap', function(evt) {
            // evt.detail.elt is the element being removed/swapped out.
            // We are interested if the taskBlock itself is this element.
            if (evt.detail.elt === taskBlock) {
                firstRect = taskBlock.getBoundingClientRect();
            } else {
                firstRect = null; // Reset if a child element caused a swap within the block
            }
        });

        taskBlock.addEventListener('htmx:afterSwap', function(evt) {
            // evt.target is the element that htmx swapped in. 
            // In this case, it should be the new taskBlock itself (since hx-target="this" or hx-target="#block-id")
            const newContentElement = evt.target;

            if (firstRect && newContentElement && newContentElement.isConnected && 
                newContentElement === taskBlock && // Ensure the event target is the block we attached listener to
                (newContentElement.classList.contains('tasks-readonly-block') || newContentElement.classList.contains('tasks-editor-form'))) {
                
                const lastRect = newContentElement.getBoundingClientRect();

                const deltaX = firstRect.left - lastRect.left;
                const deltaY = firstRect.top - lastRect.top;
                // Handle potential division by zero if new block has zero width/height briefly
                const deltaW = lastRect.width === 0 ? 1 : firstRect.width / lastRect.width;
                const deltaH = lastRect.height === 0 ? 1 : firstRect.height / lastRect.height;

                newContentElement.style.transformOrigin = 'top left';
                newContentElement.style.transform = `translate(${deltaX}px, ${translateY}px) scale(${deltaW}, ${deltaH})`;
                
                // Force reflow to apply the above style before adding transition class
                newContentElement.offsetHeight; 

                requestAnimationFrame(() => { // Use rAF for smoother start of animation
                    newContentElement.classList.add('task-block-animate-transform'); 
                    newContentElement.style.transform = ''; // Animate to natural state (identity transform)
                });

                newContentElement.addEventListener('transitionend', () => {
                    newContentElement.classList.remove('task-block-animate-transform');
                    newContentElement.style.transformOrigin = ''; // Clean up
                }, { once: true });
            }
            firstRect = null; // Reset for the next swap operation on this element
        });

        taskBlock.dataset.flipListenersAttached = 'true';
    }

    // Check if the loaded element itself is a task block
    if (elt.matches && (elt.matches('.tasks-readonly-block') || elt.matches('.tasks-editor-form'))) {
        setupFlipForTaskBlock(elt);
    }
    // Or check if it contains task blocks (e.g., if a larger container was swapped)
    const childTaskBlocks = elt.querySelectorAll ? elt.querySelectorAll('.tasks-readonly-block, .tasks-editor-form') : [];
    childTaskBlocks.forEach(setupFlipForTaskBlock);
}); 