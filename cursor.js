document.addEventListener('DOMContentLoaded', () => {
    let cursor = null;
    let rafId = null;
    let isHovering = false;

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

            // Update cursor position with RAF and transform
            document.addEventListener('mousemove', (e) => {
                if (rafId) return; // Skip if animation frame is pending
                
                rafId = requestAnimationFrame(() => {
                    // Use transform instead of left/top for better performance
                    cursor.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
                    rafId = null;
                });
            });

            // Optimize hover effects with a single class toggle
            const interactiveElements = document.querySelectorAll('a, button, .nav-button, .theme-toggle, .tool-button, .project-header, .tool-header');
            
            // Use event delegation for better performance
            document.addEventListener('mouseover', (e) => {
                const target = e.target;
                if (interactiveElements.contains(target) && !target.classList.contains('tag')) {
                    isHovering = true;
                    cursor.classList.add('hover');
                }
            });

            document.addEventListener('mouseout', (e) => {
                const target = e.target;
                if (interactiveElements.contains(target) && !target.classList.contains('tag')) {
                    isHovering = false;
                    cursor.classList.remove('hover');
                }
            });

            // Keep cursor as red dot for tags
            const tagElements = document.querySelectorAll('.tag');
            tagElements.forEach(element => {
                element.addEventListener('mouseenter', () => {
                    cursor.classList.remove('hover');
                });
            });

            // Optimize window leave/enter events
            let isVisible = true;
            document.addEventListener('mouseleave', () => {
                if (isVisible) {
                    cursor.style.opacity = '0';
                    isVisible = false;
                }
            });
            
            document.addEventListener('mouseenter', () => {
                if (!isVisible) {
                    cursor.style.opacity = '1';
                    isVisible = true;
                }
            });
        }
    }

    // Initialize cursor on load
    initCursor();

    // Optimize resize handling with debounce
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(initCursor, 100);
    });
}); 