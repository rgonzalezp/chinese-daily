// Global variable to hold the current EasyMDE instance
window.currentEasyMDE = null;
window.currentTasksMDE = null; // Added for the tasks MDE

function initializeEasyMDE() {
    var textarea = document.getElementById('notes-editor-textarea');
    if (!textarea) {
        if (window.currentEasyMDE) {
             window.currentEasyMDE = null;
        }
        var lingeringContainer = document.querySelector('.EasyMDEContainer');
        if (lingeringContainer) {
            lingeringContainer.remove();
        }
        return; 
    }

    var editorExists = false;
    if (window.currentEasyMDE) {
        try {
            if (window.currentEasyMDE.codemirror && window.currentEasyMDE.codemirror.getWrapperElement().isConnected) {
                editorExists = true;
            }
        } catch (e) {
             console.warn("Error checking existing EasyMDE instance:", e);
             window.currentEasyMDE = null;
        }
    }

    if (editorExists) {
        window.currentEasyMDE.value(textarea.value);
        var isReadOnly = textarea.disabled;
        window.currentEasyMDE.codemirror.setOption("readOnly", isReadOnly);
        var editorWrapper = window.currentEasyMDE.codemirror.getWrapperElement();
        if(isReadOnly) {
            editorWrapper.classList.add('editor-disabled');
        } else {
            editorWrapper.classList.remove('editor-disabled');
        }
    } else {
        var existingContainer = document.querySelector('.EasyMDEContainer');
        if (existingContainer) {
            existingContainer.remove();
        }
        window.currentEasyMDE = null;
        if (!textarea.disabled) {
            try {
                var easyMDE = new EasyMDE({
                    element: textarea,
                    spellChecker: true,
                    status: false,
                    lineWrapping: true,
                    onToggleFullScreen: function(fullscreen) {
                        if (!easyMDE || !easyMDE.codemirror) {
                            console.error("EasyMDE instance not available for fullscreen toggle.");
                            return;
                        }
                        const editorWrapper = easyMDE.codemirror.getWrapperElement();
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
                window.currentEasyMDE = easyMDE;
                
                easyMDE.codemirror.on('change', function() { easyMDE.codemirror.save(); });
                console.log("Notes EasyMDE Initialized successfully.");
            } catch (e) {
                console.error("Notes EasyMDE Init Error:", e);
                window.currentEasyMDE = null; 
                var failedContainer = textarea.parentNode?.querySelector('.EasyMDEContainer');
                if(failedContainer) failedContainer.remove();
            }
        } else {
             window.currentEasyMDE = null; 
        }
    }
}

function initializeTasksMDE() {
    var textarea = document.getElementById('tasks-editor-textarea');
    if (!textarea) {
        if (window.currentTasksMDE) {
             window.currentTasksMDE = null;
        }
        var lingeringContainer = document.querySelector('#tasks-editor-textarea + .EasyMDEContainer');
        if (lingeringContainer) {
            lingeringContainer.remove();
        }
        return; 
    }

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
        var existingContainer = document.querySelector('#tasks-editor-textarea + .EasyMDEContainer');
        if (existingContainer) {
            existingContainer.remove();
        }
        window.currentTasksMDE = null;
        if (!textarea.disabled) {
            try {
                var tasksMDE = new EasyMDE({
                    element: textarea,
                    spellChecker: true,
                    status: false,
                    lineWrapping: true,
                    onToggleFullScreen: function(fullscreen) {
                        if (!tasksMDE || !tasksMDE.codemirror) {
                            console.error("Tasks MDE - EasyMDE instance not available for fullscreen toggle.");
                            return;
                        }
                        const editorWrapper = tasksMDE.codemirror.getWrapperElement();
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
                window.currentTasksMDE = tasksMDE;
                
                tasksMDE.codemirror.on('change', function() { tasksMDE.codemirror.save(); });
                console.log("Tasks MDE - Initialized successfully.");
            } catch (e) {
                console.error("Tasks MDE - Init Error:", e);
                window.currentTasksMDE = null; 
                var failedContainer = textarea.parentNode?.querySelector('.EasyMDEContainer');
                if(failedContainer) failedContainer.remove();
            }
        } else {
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
            const newContentElement = evt.target;

            // CRUCIAL GUARD: Only proceed if firstRect was captured for THIS swap sequence
            // and the swapped element is the one we are tracking.
            if (firstRect && newContentElement && newContentElement.isConnected && 
                newContentElement === taskBlock && 
                (newContentElement.classList.contains('tasks-readonly-block') || newContentElement.classList.contains('tasks-editor-form'))) {
                
                const lastRect = newContentElement.getBoundingClientRect();

                const deltaX = firstRect.left - lastRect.left;
                const deltaY = firstRect.top - lastRect.top; // This should now be safe
                const deltaW = lastRect.width === 0 ? 1 : firstRect.width / lastRect.width;
                const deltaH = lastRect.height === 0 ? 1 : firstRect.height / lastRect.height;

                newContentElement.style.transformOrigin = 'top left';
                // Check if any delta is NaN or undefined before applying to avoid invalid transform string
                if (![deltaX, deltaY, deltaW, deltaH].some(isNaN) && [deltaX, deltaY, deltaW, deltaH].every(val => typeof val === 'number')) {
                    newContentElement.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(${deltaW}, ${deltaH})`;
                } else {
                    console.warn('FLIP animation: Invalid delta values. Skipping initial transform.', 
                                 {deltaX, deltaY, deltaW, deltaH});
                    // Optionally, still attempt to animate to identity if deltas are bad but element is new
                    // newContentElement.style.transform = ''; // Or some safe default
                }
                
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