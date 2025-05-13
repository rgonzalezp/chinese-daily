document.addEventListener('DOMContentLoaded', () => {
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'preview-modal-overlay';
    // modalOverlay.style.display = 'none'; // Controlled by active class now

    const modalContent = document.createElement('div');
    modalContent.className = 'preview-modal-content';

    const closeModalButton = document.createElement('button');
    closeModalButton.className = 'preview-modal-close-btn';
    closeModalButton.textContent = 'Close';
    
    // Structure: Overlay contains Content, and Close Button is sibling to Content for positioning
    modalOverlay.appendChild(modalContent);
    modalOverlay.appendChild(closeModalButton); 
    document.body.appendChild(modalOverlay);

    let originalParent = null;
    let originalIframeStyles = { width: '', height: '' }; // Store original iframe dimensions if needed
    let activeIframe = null;
    let activeIframeOriginalThemeId = null; // Store the theme ID for reset

    document.querySelectorAll('.expand-preview-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); 
            event.stopPropagation(); 

            const iframeId = button.dataset.iframeId;
            const themeIdForPreview = button.dataset.themeId; // Get the theme ID
            activeIframe = document.getElementById(iframeId);
            activeIframeOriginalThemeId = themeIdForPreview; // Store for reset on close

            if (activeIframe) {
                originalParent = activeIframe.parentNode;
                originalIframeStyles.width = activeIframe.style.width;
                originalIframeStyles.height = activeIframe.style.height;

                // Set iframe src to include the preview_theme parameter
                if (themeIdForPreview) {
                    activeIframe.src = `/?preview_theme=${themeIdForPreview}`;
                } else {
                    activeIframe.src = '/'; // Fallback if no themeId found
                }

                modalContent.appendChild(activeIframe); 
                activeIframe.style.width = '100%'; 
                activeIframe.style.height = '100%';
                // modalOverlay.style.display = 'flex'; 
                modalOverlay.classList.add('active'); // Show modal via class
            }
        });
    });

    function closeTheModal() {
        if (activeIframe && originalParent) {
            originalParent.appendChild(activeIframe); 
            activeIframe.style.width = originalIframeStyles.width;
            activeIframe.style.height = originalIframeStyles.height;
            // Reset iframe src to its original card-specific theme URL
            if (activeIframeOriginalThemeId) {
                activeIframe.src = `/?preview_theme=${activeIframeOriginalThemeId}`;
            } else {
                activeIframe.src = '/'; // Fallback, though should have themeId
            }
        }
        // modalOverlay.style.display = 'none';
        modalOverlay.classList.remove('active'); // Hide modal via class
        activeIframe = null;
        originalParent = null;
        activeIframeOriginalThemeId = null; // Clear stored themeId
    }

    closeModalButton.addEventListener('click', closeTheModal);

    modalOverlay.addEventListener('click', (event) => {
        if (event.target === modalOverlay) {
            closeTheModal();
        }
    });
}); 