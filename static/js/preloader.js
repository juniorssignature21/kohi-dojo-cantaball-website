/**
 * KOHI DOJO CANTABALL LEAGUE - Preloader Script
 * Manages the loading state and animation
 */

(function () {
  'use strict';

  // Preloader initialization
  function initPreloader() {
    const preloader = document.getElementById('page-preloader');
    
    if (!preloader) return;

    // Simulate minimum loading time for visual effect
    const minLoadTime = 800; // milliseconds
    const startTime = Date.now();

    // Hide preloader when page is fully loaded
    function hidePreloader() {
      const elapsedTime = Date.now() - startTime;
      const delayNeeded = Math.max(0, minLoadTime - elapsedTime);

      setTimeout(() => {
        if (preloader) {
          preloader.classList.add('hidden');
          
          // Optional: Remove from DOM after fade out
          setTimeout(() => {
            if (preloader.parentNode) {
              preloader.parentNode.removeChild(preloader);
            }
          }, 600);
        }
      }, delayNeeded);
    }

    // Listen for various page load events
    if (document.readyState === 'loading') {
      // Page still loading
      document.addEventListener('DOMContentLoaded', hidePreloader);
      window.addEventListener('load', hidePreloader);
    } else {
      // Page already loaded
      hidePreloader();
    }

    // Fallback: hide preloader after max 5 seconds
    setTimeout(() => {
      if (preloader && !preloader.classList.contains('hidden')) {
        hidePreloader();
      }
    }, 5000);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPreloader);
  } else {
    initPreloader();
  }
})();
