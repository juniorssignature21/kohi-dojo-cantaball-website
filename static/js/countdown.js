/**
 * KOHI DOJO CANTABALL LEAGUE - Countdown Timer
 * Handles: Registration countdown, progress bar updates
 */

(function () {
  'use strict';

  /* ==========================================
     COUNTDOWN TIMER
     ========================================== */
  function initCountdown() {
    const countdownContainers = document.querySelectorAll('[data-countdown]');
    if (!countdownContainers.length) return;

    countdownContainers.forEach((container) => {
      const targetDateStr = container.getAttribute('data-countdown');
      if (!targetDateStr) return;

      const targetDate = new Date(targetDateStr).getTime();
      const daysEl = container.querySelector('[data-countdown-days]');
      const hoursEl = container.querySelector('[data-countdown-hours]');
      const minsEl = container.querySelector('[data-countdown-minutes]');
      const secsEl = container.querySelector('[data-countdown-seconds]');

      function pad(num) {
        return num.toString().padStart(2, '0');
      }

      function update() {
        const now = new Date().getTime();
        const diff = targetDate - now;

        if (diff <= 0) {
          // Countdown expired
          if (daysEl) daysEl.textContent = '00';
          if (hoursEl) hoursEl.textContent = '00';
          if (minsEl) minsEl.textContent = '00';
          if (secsEl) secsEl.textContent = '00';

          // Show expired message if exists
          const expiredMsg = container.querySelector('[data-countdown-expired]');
          if (expiredMsg) {
            expiredMsg.style.display = 'block';
            container.querySelector('.countdown').style.display = 'none';
          }
          return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        if (daysEl) daysEl.textContent = pad(days);
        if (hoursEl) hoursEl.textContent = pad(hours);
        if (minsEl) minsEl.textContent = pad(minutes);
        if (secsEl) secsEl.textContent = pad(seconds);
      }

      // Update immediately and then every second
      update();
      setInterval(update, 1000);
    });
  }

  /* ==========================================
     PROGRESS BAR ANIMATION
     ========================================== */
  function initProgressBars() {
    const progressBars = document.querySelectorAll('[data-progress]');
    if (!progressBars.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const bar = entry.target;
            const target = bar.getAttribute('data-progress');
            const fill = bar.querySelector('.progress-fill');
            if (fill) {
              setTimeout(() => {
                fill.style.width = target + '%';
              }, 200);
            }
            observer.unobserve(bar);
          }
        });
      },
      { threshold: 0.5 }
    );

    progressBars.forEach((bar) => observer.observe(bar));
  }

  /* ==========================================
     INITIALIZE
     ========================================== */
  function init() {
    initCountdown();
    initProgressBars();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
