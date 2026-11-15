(() => {
    const storageKey = 'sigoa_theme';

    function applyTheme(theme, persist = false) {
        const isDark = theme === 'dark';
        document.documentElement.classList.toggle('dark-mode', isDark);
        if (persist) {
            try { localStorage.setItem(storageKey, isDark ? 'dark' : 'light'); } catch (error) {}
        }

        document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
            button.setAttribute('aria-pressed', String(isDark));
            button.setAttribute('aria-label', isDark ? 'Ativar modo claro' : 'Ativar modo escuro');
            button.title = isDark ? 'Ativar modo claro' : 'Ativar modo escuro';
            button.replaceChildren();
            const icon = document.createElement('i');
            icon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
            icon.className = 'w-4 h-4';
            button.append(icon);
        });
        if (window.lucide) {
            window.lucide.createIcons();
        } else {
            document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
                button.textContent = isDark ? '☀' : '☾';
            });
        }
    }

    let savedTheme = 'light';
    try {
        if (localStorage.getItem(storageKey) === 'dark') savedTheme = 'dark';
    } catch (error) {}
    applyTheme(savedTheme);

    document.addEventListener('click', (event) => {
        const button = event.target.closest('[data-theme-toggle]');
        if (!button) return;
        const isDark = document.documentElement.classList.contains('dark-mode');
        applyTheme(isDark ? 'light' : 'dark', true);
    });
})();
