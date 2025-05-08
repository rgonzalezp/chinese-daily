document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const templatesContainer = document.querySelector('.templates-container');
    // Duration of the cascadeOut animation + longest delay, or a bit more for safety
    // Longest delay is 0.3s, animation is 0.3s. Total ~0.6s. Let's use 650ms.
    const closingAnimationDuration = 650; 
    let closingTimeout = null;

    if (!sidebar || !templatesContainer) {
        console.warn('Sidebar or templates container not found. Sidebar interactions will not be initialized.');
        return;
    }

    function openMenu() {
        // Clear any pending closing actions
        if (closingTimeout) {
            clearTimeout(closingTimeout);
            closingTimeout = null;
        }
        templatesContainer.classList.remove('menu-closing');
        templatesContainer.classList.add('menu-open');
    }

    function closeMenu() {
        if (templatesContainer.classList.contains('menu-open')) {
            templatesContainer.classList.remove('menu-open');
            templatesContainer.classList.add('menu-closing');
            
            // Clear any existing timeout to prevent premature removal of menu-closing
            if (closingTimeout) {
                clearTimeout(closingTimeout);
            }

            closingTimeout = setTimeout(() => {
                templatesContainer.classList.remove('menu-closing');
                closingTimeout = null;
            }, closingAnimationDuration);
        }
    }

    templatesContainer.addEventListener('mouseenter', openMenu);
    sidebar.addEventListener('mouseleave', closeMenu);

    // Close menu on click of a main sidebar button or a weekday link
    sidebar.addEventListener('click', (event) => {
        // Check if the clicked element or its parent is a button that should close the menu
        const clickedButton = event.target.closest('.sidebar-button, .sidebar-today-button');
        
        if (clickedButton) {
            // Check if the button is NOT the templates dropdown button itself
            // and if it's inside the sidebar (which it should be by this point).
            // Also, check if it's one of the weekday buttons inside the templates container.
            const isTemplatesDropdownButton = clickedButton.classList.contains('templates-dropdown-button');
            const isWeekdayButton = clickedButton.classList.contains('weekday-button') && templatesContainer.contains(clickedButton);

            if (!isTemplatesDropdownButton || isWeekdayButton) {
                // Close if it's a weekday button OR any other sidebar button (excluding the main templates toggle)
                // OR if it's the today button.
                closeMenu();
            }
        }
    });

    // More event listeners will be added here in the next steps.
    console.log('Sidebar interactions script loaded and elements found.'); // For testing

}); 