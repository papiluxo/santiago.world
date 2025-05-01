document.addEventListener('DOMContentLoaded', () => {
    let cursor = null;

    function initCursor() {
        // Remove existing cursor if any
        if (cursor) {
            cursor.remove();
        }

        // Only initialize custom cursor on desktop
        if (window.innerWidth >= 769) {
            // Create cursor element
            cursor = document.createElement('div');
            cursor.className = 'custom-cursor';
            document.body.appendChild(cursor);

            // Update cursor position
            document.addEventListener('mousemove', (e) => {
                requestAnimationFrame(() => {
                    cursor.style.left = e.clientX + 'px';
                    cursor.style.top = e.clientY + 'px';
                });
            });

            // Add hover effect only for non-tag interactive elements
            const interactiveElements = document.querySelectorAll('a, button, .nav-button, .theme-toggle, .tool-button, .project-header, .tool-header');
            interactiveElements.forEach(element => {
                element.addEventListener('mouseenter', () => {
                    cursor.classList.add('hover');
                });
                element.addEventListener('mouseleave', () => {
                    cursor.classList.remove('hover');
                });
            });

            // Keep cursor as red dot for tags
            const tagElements = document.querySelectorAll('.tag');
            tagElements.forEach(element => {
                element.addEventListener('mouseenter', () => {
                    cursor.classList.remove('hover');
                });
            });

            // Hide cursor when leaving window
            document.addEventListener('mouseleave', () => {
                cursor.style.display = 'none';
            });
            document.addEventListener('mouseenter', () => {
                cursor.style.display = 'block';
            });
        }
    }

    // Initialize cursor on load
    initCursor();

    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(initCursor, 100);
    });
}); 