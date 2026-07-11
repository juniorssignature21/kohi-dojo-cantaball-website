/**
 * KOHI DOJO CANTABALL LEAGUE - Dashboard JavaScript
 * Handles: Sidebar toggle, charts (canvas), action buttons, responsive
 */

(function () {
  'use strict';

  /* ==========================================
     SIDEBAR TOGGLE (Mobile)
     ========================================== */
  function initSidebarToggle() {
    const toggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.dashboard-sidebar');
    if (!toggle || !sidebar) return;

    // Create overlay
    let overlay = document.querySelector('.sidebar-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'sidebar-overlay';
      overlay.style.cssText =
        'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:99;display:none;';
      document.body.appendChild(overlay);
    }

    function openSidebar() {
      sidebar.classList.add('open');
      overlay.style.display = 'block';
      document.body.style.overflow = 'hidden';
    }

    function closeSidebar() {
      sidebar.classList.remove('open');
      overlay.style.display = 'none';
      document.body.style.overflow = '';
    }

    toggle.addEventListener('click', () => {
      if (sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener('click', closeSidebar);

    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && sidebar.classList.contains('open')) {
        closeSidebar();
      }
    });

    // Close sidebar when clicking a nav link on mobile
    sidebar.querySelectorAll('.sidebar-nav a').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          closeSidebar();
        }
      });
    });
  }

  /* ==========================================
     REGISTRATION BAR CHART
     ========================================== */
  function initRegistrationChart() {
    const canvas = document.getElementById('registrationChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const data = [12, 16, 14, 18, 20]; // Week 1-5 registrations
    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'];
    const maxVal = 25;

    function draw() {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const width = rect.width;
      const height = rect.height;
      const padding = { top: 20, right: 20, bottom: 40, left: 40 };
      const chartWidth = width - padding.left - padding.right;
      const chartHeight = height - padding.top - padding.bottom;

      ctx.clearRect(0, 0, width, height);

      // Y-axis grid lines
      const ySteps = 5;
      for (let i = 0; i <= ySteps; i++) {
        const y = padding.top + (chartHeight / ySteps) * i;
        const value = Math.round(maxVal - (maxVal / ySteps) * i);

        ctx.beginPath();
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.3)';
        ctx.lineWidth = 1;
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();

        // Y-axis labels
        ctx.fillStyle = '#94A3B8';
        ctx.font = '11px Poppins';
        ctx.textAlign = 'right';
        ctx.fillText(value, padding.left - 8, y + 4);
      }

      // Bars
      const barWidth = chartWidth / data.length * 0.5;
      const barGap = chartWidth / data.length;

      data.forEach((value, index) => {
        const barHeight = (value / maxVal) * chartHeight;
        const x = padding.left + barGap * index + (barGap - barWidth) / 2;
        const y = padding.top + chartHeight - barHeight;

        // Bar gradient
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, '#EA580C');
        gradient.addColorStop(1, '#F59E0B');

        // Rounded top corners
        const radius = 6;
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + barWidth - radius, y);
        ctx.quadraticCurveTo(x + barWidth, y, x + barWidth, y + radius);
        ctx.lineTo(x + barWidth, y + barHeight);
        ctx.lineTo(x, y + barHeight);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
        ctx.fillStyle = gradient;
        ctx.fill();

        // Value label on top
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '600 12px Poppins';
        ctx.textAlign = 'center';
        ctx.fillText(value, x + barWidth / 2, y - 8);

        // X-axis label
        ctx.fillStyle = '#94A3B8';
        ctx.font = '12px Poppins';
        ctx.textAlign = 'center';
        ctx.fillText(labels[index], x + barWidth / 2, height - 10);
      });
    }

    draw();
    window.addEventListener('resize', draw);
  }

  /* ==========================================
     PAYMENT LINE CHART
     ========================================== */
  function initPaymentChart() {
    const canvas = document.getElementById('paymentChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const data = [60000, 80000, 70000, 90000, 100000]; // Revenue per week
    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'];
    const maxVal = 120000;

    function formatCurrency(val) {
      if (val >= 1000) {
        return '₦' + (val / 1000) + 'K';
      }
      return '₦' + val;
    }

    function draw() {
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);

      const width = rect.width;
      const height = rect.height;
      const padding = { top: 20, right: 20, bottom: 40, left: 55 };
      const chartWidth = width - padding.left - padding.right;
      const chartHeight = height - padding.top - padding.bottom;

      ctx.clearRect(0, 0, width, height);

      // Y-axis grid lines
      const ySteps = 5;
      for (let i = 0; i <= ySteps; i++) {
        const y = padding.top + (chartHeight / ySteps) * i;
        const value = Math.round(maxVal - (maxVal / ySteps) * i);

        ctx.beginPath();
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.3)';
        ctx.lineWidth = 1;
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();

        // Y-axis labels
        ctx.fillStyle = '#94A3B8';
        ctx.font = '10px Poppins';
        ctx.textAlign = 'right';
        ctx.fillText(formatCurrency(value), padding.left - 8, y + 4);
      }

      // Calculate points
      const points = data.map((value, index) => ({
        x: padding.left + (chartWidth / (data.length - 1)) * index,
        y: padding.top + chartHeight - (value / maxVal) * chartHeight,
      }));

      // Area fill
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      points.forEach((p) => ctx.lineTo(p.x, p.y));
      ctx.lineTo(points[points.length - 1].x, padding.top + chartHeight);
      ctx.lineTo(points[0].x, padding.top + chartHeight);
      ctx.closePath();

      const areaGradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight);
      areaGradient.addColorStop(0, 'rgba(230, 57, 70, 0.2)');
      areaGradient.addColorStop(1, 'rgba(230, 57, 70, 0)');
      ctx.fillStyle = areaGradient;
      ctx.fill();

      // Line
      ctx.beginPath();
      ctx.moveTo(points[0].x, points[0].y);
      points.forEach((p) => ctx.lineTo(p.x, p.y));
      ctx.strokeStyle = '#EA580C';
      ctx.lineWidth = 3;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      ctx.stroke();

      // Points
      points.forEach((p, index) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#EA580C';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
        ctx.fillStyle = '#0F172A';
        ctx.fill();

        // Value label
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '600 11px Poppins';
        ctx.textAlign = 'center';
        ctx.fillText(formatCurrency(data[index]), p.x, p.y - 12);

        // X-axis label
        ctx.fillStyle = '#94A3B8';
        ctx.font = '12px Poppins';
        ctx.fillText(labels[index], p.x, height - 10);
      });
    }

    draw();
    window.addEventListener('resize', draw);
  }

  /* ==========================================
     ACTION BUTTON HANDLERS
     ========================================== */
  function initActionButtons() {
    // Open Registration
    const openRegBtn = document.querySelector('[data-action="open-registration"]');
    if (openRegBtn) {
      openRegBtn.addEventListener('click', function () {
        setButtonLoading(this, 'Opening...');
        setTimeout(() => {
          resetButton(this);
          showNotification('Registration opened successfully!', 'success');
        }, 1000);
      });
    }

    // Close Registration
    const closeRegBtn = document.querySelector('[data-action="close-registration"]');
    if (closeRegBtn) {
      closeRegBtn.addEventListener('click', function () {
        if (confirm('Are you sure you want to close registration?')) {
          setButtonLoading(this, 'Closing...');
          setTimeout(() => {
            resetButton(this);
            showNotification('Registration closed!', 'warning');
          }, 1000);
        }
      });
    }

    // Generate Fixtures
    const genFixturesBtn = document.querySelector('[data-action="generate-fixtures"]');
    if (genFixturesBtn) {
      genFixturesBtn.addEventListener('click', function () {
        setButtonLoading(this, 'Generating...');
        setTimeout(() => {
          resetButton(this);
          showNotification('Fixtures generated for Week 5!', 'success');
        }, 1500);
      });
    }

    // Export Data
    const exportBtn = document.querySelector('[data-action="export-data"]');
    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        showNotification('Data export started...', 'info');
        setTimeout(() => {
          showNotification('Data exported successfully!', 'success');
        }, 1000);
      });
    }
  }

  /* ==========================================
     NOTIFICATION TOAST
     ========================================== */
  function showNotification(message, type) {
    let container = document.querySelector('.notification-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'notification-container';
      container.style.cssText =
        'position:fixed;top:24px;right:24px;z-index:400;display:flex;flex-direction:column;gap:8px;';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const colors = {
      success: '#10B981',
      warning: '#F59E0B',
      danger: '#EF4444',
      info: '#3B82F6',
    };
    const icons = {
      success: 'fa-check-circle',
      warning: 'fa-exclamation-triangle',
      danger: 'fa-times-circle',
      info: 'fa-info-circle',
    };

    toast.style.cssText = `
      background: #1E293B;
      border: 1px solid ${colors[type] || colors.info};
      border-radius: 12px;
      padding: 16px 20px;
      color: #FFFFFF;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
      animation: slideInRight 0.3s ease;
      min-width: 280px;
    `;
    toast.innerHTML = `
      <i class="fas ${icons[type] || icons.info}" style="color: ${colors[type] || colors.info};"></i>
      <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOutRight 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // Add toast animations
  if (!document.getElementById('toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
      @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }

  /* ==========================================
     TABLE SEARCH
     ========================================== */
  function initTableSearch() {
    const searchInputs = document.querySelectorAll('[data-table-search]');
    searchInputs.forEach((input) => {
      const tableId = input.getAttribute('data-table-search');
      const table = document.getElementById(tableId);
      if (!table) return;

      input.addEventListener('input', () => {
        const query = input.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach((row) => {
          const text = row.textContent.toLowerCase();
          row.style.display = text.includes(query) ? '' : 'none';
        });
      });
    });
  }

  /* ==========================================
     BUTTON HELPERS
     ========================================== */
  function setButtonLoading(btn, text) {
    btn.dataset.originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> ' + (text || 'Loading...');
    btn.disabled = true;
  }

  function resetButton(btn) {
    if (btn.dataset.originalText) {
      btn.innerHTML = btn.dataset.originalText;
    }
    btn.disabled = false;
  }

  /* ==========================================
     INITIALIZE
     ========================================== */
  function init() {
    initSidebarToggle();
    initRegistrationChart();
    initPaymentChart();
    initActionButtons();
    initTableSearch();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
