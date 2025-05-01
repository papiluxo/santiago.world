document.addEventListener('DOMContentLoaded', () => {
    // Only initialize custom cursor on desktop
    if (window.innerWidth >= 769) {
        // Create cursor element
        const cursor = document.createElement('div');
        cursor.className = 'custom-cursor';
        document.body.appendChild(cursor);

        // Update cursor position
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        // Add hover effect
        const interactiveElements = document.querySelectorAll('a, button, .nav-button, .theme-toggle, .tool-button, .project-header, .tool-header');
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                cursor.classList.add('hover');
            });
            element.addEventListener('mouseleave', () => {
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
}); 