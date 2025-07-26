// theme-toggle.js
(function() {
    const html = document.documentElement;
    const btn = document.getElementById('theme-toggle');
    const darkClass = 'dark';
    const storageKey = 'lingua-theme';

    function setTheme(dark) {
        if (dark) {
            html.classList.add(darkClass);
            localStorage.setItem(storageKey, 'dark');
        } else {
            html.classList.remove(darkClass);
            localStorage.setItem(storageKey, 'light');
        }
    }

    // Автоопределение темы при первом заходе
    function getPreferredTheme() {
        const saved = localStorage.getItem(storageKey);
        if (saved) return saved === 'dark';
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    // Инициализация
    setTheme(getPreferredTheme());

    if (btn) {
        btn.addEventListener('click', function() {
            setTheme(!html.classList.contains(darkClass));
        });
    }
})(); 