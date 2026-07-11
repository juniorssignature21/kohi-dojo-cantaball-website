/**
 * KOHI DOJO CANTABALL LEAGUE - Navbar JavaScript
 * Handles: Active nav link highlighting, mobile menu enhancements
 */

(function () {
  'use strict';

  /* ==========================================
     ACTIVE NAV LINK HIGHLIGHTING
     ========================================== */
  function initActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.header-nav a, .mobile-menu a');

    navLinks.forEach((link) => {
      const href = link.getAttribute('href');
      if (!href) return;

      // Check if the current path matches the link
      if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  /* ==========================================
     MOBILE MENU SCROLL LOCK
     ========================================== */
  function initMobileMenuScrollLock() {
    const toggle = document.querySelector('.mobile-toggle');
    const menu = document.querySelector('.mobile-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', () => {
      if (menu.classList.contains('open')) {
        document.body.style.overflow = '';
      } else {
        document.body.style.overflow = 'hidden';
      }
    });

    // Also close menu and unlock scroll when clicking a link
    menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        document.body.style.overflow = '';
      });
    });
  }

  /* ==========================================
     HEADER HIDE/SHOW ON SCROLL (optional)
     ========================================== */
  function initHeaderSmartHide() {
    const header = document.querySelector('.header');
    if (!header) return;

    let lastScrollY = 0;
    let ticking = false;

    function updateHeader() {
      const scrollY = window.scrollY;

      // Don't hide if mobile menu is open
      const mobileMenu = document.querySelector('.mobile-menu');
      if (mobileMenu && mobileMenu.classList.contains('open')) {
        ticking = false;
        return;
      }

      if (scrollY > lastScrollY && scrollY > 200) {
        // Scrolling down
        header.style.transform = 'translateY(-100%)';
      } else {
        // Scrolling up
        header.style.transform = 'translateY(0)';
      }

      lastScrollY = scrollY;
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateHeader);
        ticking = true;
      }
    });

    // Add transition for smooth hide/show
    header.style.transition = 'transform 0.3s ease, background 0.3s ease, border-color 0.3s ease';
  }

  /* ==========================================
     INITIALIZE
     ========================================== */
  function init() {
    initActiveNavLink();
    initMobileMenuScrollLock();
    initHeaderSmartHide();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
