/**
 * KOHI DOJO CANTABALL LEAGUE - Main Application JavaScript
 * Handles: Scroll animations, navbar, back-to-top, mobile menu, smooth scroll
 */

(function () {
  'use strict';

  /* ==========================================
     SCROLL-TRIGGERED ANIMATIONS
     ========================================== */
  function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-left, .slide-right');
    if (!animatedElements.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );

    animatedElements.forEach((el) => observer.observe(el));
  }

  /* ==========================================
     HEADER SCROLL EFFECT
     ========================================== */
  function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;

    let ticking = false;

    function updateHeader() {
      const scrollY = window.scrollY;
      if (scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(updateHeader);
        ticking = true;
      }
    });

    // Initial check
    updateHeader();
  }

  /* ==========================================
     BACK TO TOP BUTTON
     ========================================== */
  function initBackToTop() {
    const btn = document.querySelector('.back-to-top');
    if (!btn) return;

    let ticking = false;

    function toggleBtn() {
      if (window.scrollY > 300) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(toggleBtn);
        ticking = true;
      }
    });

    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ==========================================
     MOBILE MENU TOGGLE
     ========================================== */
  function initMobileMenu() {
    const toggle = document.querySelector('.mobile-toggle');
    const menu = document.querySelector('.mobile-menu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', () => {
      menu.classList.toggle('open');
      const icon = toggle.querySelector('i');
      if (menu.classList.contains('open')) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-xmark');
      } else {
        icon.classList.remove('fa-xmark');
        icon.classList.add('fa-bars');
      }
    });

    // Close menu when clicking a link
    menu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        menu.classList.remove('open');
        const icon = toggle.querySelector('i');
        icon.classList.remove('fa-xmark');
        icon.classList.add('fa-bars');
      });
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && menu.classList.contains('open')) {
        menu.classList.remove('open');
        const icon = toggle.querySelector('i');
        icon.classList.remove('fa-xmark');
        icon.classList.add('fa-bars');
      }
    });
  }

  /* ==========================================
     SMOOTH SCROLL FOR ANCHOR LINKS
     ========================================== */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', function (e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;

        const target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          const headerOffset = 80;
          const elementPosition = target.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth',
          });
        }
      });
    });
  }

  /* ==========================================
     STATS COUNTER ANIMATION
     ========================================== */
  function initStatsCounter() {
    const statNumbers = document.querySelectorAll('.stat-number[data-count]');
    if (!statNumbers.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );

    statNumbers.forEach((el) => observer.observe(el));
  }

  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-count'), 10);
    const duration = 2000;
    const start = performance.now();
    const prefix = el.getAttribute('data-prefix') || '';
    const suffix = el.getAttribute('data-suffix') || '';

    function update(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = Math.round(eased * target);
      el.textContent = prefix + current.toLocaleString() + suffix;

      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }

    requestAnimationFrame(update);
  }

  /* ==========================================
     GALLERY LIGHTBOX
     ========================================== */
  function initLightbox() {
    const galleryItems = document.querySelectorAll('[data-lightbox]');
    if (!galleryItems.length) return;

    let currentIndex = 0;
    const images = Array.from(galleryItems).map((item) => ({
      src: item.getAttribute('data-lightbox'),
      caption: item.getAttribute('data-caption') || '',
    }));

    // Create modal if not exists
    let modal = document.querySelector('.lightbox-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.className = 'modal-overlay lightbox-modal';
      modal.innerHTML = `
        <div class="modal-content">
          <button class="modal-close" aria-label="Close"><i class="fas fa-xmark"></i></button>
          <button class="modal-nav prev" aria-label="Previous"><i class="fas fa-chevron-left"></i></button>
          <img src="" alt="Gallery image" style="max-width:100%;max-height:80vh;border-radius:12px;">
          <button class="modal-nav next" aria-label="Next"><i class="fas fa-chevron-right"></i></button>
          <span class="modal-counter">1 / ${images.length}</span>
        </div>
      `;
      document.body.appendChild(modal);
    }

    const modalImg = modal.querySelector('img');
    const modalCounter = modal.querySelector('.modal-counter');
    const modalClose = modal.querySelector('.modal-close');
    const modalPrev = modal.querySelector('.modal-nav.prev');
    const modalNext = modal.querySelector('.modal-nav.next');

    function openModal(index) {
      currentIndex = index;
      modalImg.src = images[currentIndex].src;
      modalCounter.textContent = `${currentIndex + 1} / ${images.length}`;
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }

    function prevImage() {
      currentIndex = (currentIndex - 1 + images.length) % images.length;
      modalImg.src = images[currentIndex].src;
      modalCounter.textContent = `${currentIndex + 1} / ${images.length}`;
    }

    function nextImage() {
      currentIndex = (currentIndex + 1) % images.length;
      modalImg.src = images[currentIndex].src;
      modalCounter.textContent = `${currentIndex + 1} / ${images.length}`;
    }

    galleryItems.forEach((item, index) => {
      item.addEventListener('click', () => openModal(index));
    });

    modalClose.addEventListener('click', closeModal);
    modalPrev.addEventListener('click', (e) => {
      e.stopPropagation();
      prevImage();
    });
    modalNext.addEventListener('click', (e) => {
      e.stopPropagation();
      nextImage();
    });
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });

    document.addEventListener('keydown', (e) => {
      if (!modal.classList.contains('active')) return;
      if (e.key === 'Escape') closeModal();
      if (e.key === 'ArrowLeft') prevImage();
      if (e.key === 'ArrowRight') nextImage();
    });
  }

  /* ==========================================
     FAQ ACCORDION
     ========================================== */
  function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    if (!faqItems.length) return;

    faqItems.forEach((item) => {
      const header = item.querySelector('.faq-header');
      if (!header) return;

      header.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');

        // Close all others (optional - remove for multiple open)
        faqItems.forEach((other) => other.classList.remove('open'));

        if (!isOpen) {
          item.classList.add('open');
        }
      });
    });
  }

  /* ==========================================
     PARTICLE NETWORK (Hero Background)
     ========================================== */
  function initParticleNetwork() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    let mouse = { x: null, y: null };

    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 25 : 50;
    const connectionDistance = 150;
    const mouseDistance = 200;

    function resize() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }

    function createParticles() {
      particles = [];
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1,
        });
      }
    }

    function drawParticles() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update positions
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      });

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDistance) {
            const opacity = 1 - dist / connectionDistance;
            ctx.beginPath();
            ctx.strokeStyle = `rgba(230, 57, 70, ${opacity * 0.3})`;
            ctx.lineWidth = 1;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }

        // Mouse connections
        if (mouse.x !== null && mouse.y !== null) {
          const dx = particles[i].x - mouse.x;
          const dy = particles[i].y - mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < mouseDistance) {
            const opacity = 1 - dist / mouseDistance;
            ctx.beginPath();
            ctx.strokeStyle = `rgba(230, 57, 70, ${opacity * 0.5})`;
            ctx.lineWidth = 1;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(mouse.x, mouse.y);
            ctx.stroke();
          }
        }
      }

      // Draw particles
      particles.forEach((p) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(230, 57, 70, 0.6)';
        ctx.fill();
      });

      animationId = requestAnimationFrame(drawParticles);
    }

    // Mouse tracking
    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left;
      mouse.y = e.clientY - rect.top;
    });

    canvas.addEventListener('mouseleave', () => {
      mouse.x = null;
      mouse.y = null;
    });

    // Initialize
    resize();
    createParticles();
    drawParticles();

    window.addEventListener('resize', () => {
      resize();
      createParticles();
    });

    // Cleanup on page hide
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        cancelAnimationFrame(animationId);
      } else {
        drawParticles();
      }
    });
  }

  /* ==========================================
     GALLERY FILTER TABS
     ========================================== */
  function initGalleryFilter() {
    const tabs = document.querySelectorAll('.gallery-filter-tab');
    const items = document.querySelectorAll('.gallery-filter-item');
    if (!tabs.length || !items.length) return;

    tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const filter = tab.getAttribute('data-filter');

        tabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');

        items.forEach((item) => {
          const category = item.getAttribute('data-category');
          if (filter === 'all' || category === filter) {
            item.style.display = '';
            item.classList.add('fade-in');
            setTimeout(() => item.classList.add('visible'), 50);
          } else {
            item.style.display = 'none';
          }
        });
      });
    });
  }

  /* ==========================================
     BUTTON LOADING STATE
     ========================================== */
  window.setButtonLoading = function (btn, loadingText) {
    btn.dataset.originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> ' + (loadingText || 'Loading...');
    btn.disabled = true;
  };

  window.resetButton = function (btn) {
    if (btn.dataset.originalText) {
      btn.innerHTML = btn.dataset.originalText;
    }
    btn.disabled = false;
  };

  /* ==========================================
     INITIALIZE ALL
     ========================================== */
  function init() {
    initScrollAnimations();
    initHeaderScroll();
    initBackToTop();
    initMobileMenu();
    initSmoothScroll();
    initStatsCounter();
    initLightbox();
    initFaqAccordion();
    initParticleNetwork();
    initGalleryFilter();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
