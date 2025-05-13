// static/js/apply_theme.js
(function() {
    // This script expects `window.themeToApply` to be set before it runs.
    const themeId = window.themeToApply;

    if (!themeId || !themeId.startsWith('theme-')) {
        console.error('[ApplyTheme] Invalid or missing theme ID:', themeId);
        return;
    }

    console.log('[ApplyTheme] Applying theme:', themeId);
    const rootEl = document.documentElement;

    // Remove any existing theme classes from <html>
    rootEl.className = rootEl.className.replace(/theme-\S+/g, '').trim();

    // Add the new theme class to <html>
    rootEl.classList.add(themeId);

    // Save the theme choice in localStorage for persistence
    localStorage.setItem('selectedTheme', themeId);

    // Clean up the global variable
    delete window.themeToApply;
})(); 