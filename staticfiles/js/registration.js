/**
 * KOHI DOJO CANTABALL LEAGUE - Registration JavaScript
 * Handles: Form validation, image preview, payment interactions
 */

(function () {
  'use strict';

  /* ==========================================
     FORM VALIDATION
     ========================================== */
  function initFormValidation() {
    const forms = document.querySelectorAll('[data-validate]');
    if (!forms.length) return;

    forms.forEach((form) => {
      const inputs = form.querySelectorAll('input[data-validate], textarea[data-validate], select[data-validate]');

      inputs.forEach((input) => {
        // Validate on blur
        input.addEventListener('blur', () => validateField(input));

        // Clear error on input
        input.addEventListener('input', () => {
          input.classList.remove('error');
          const errorEl = input.parentNode.querySelector('.form-error');
          if (errorEl) errorEl.style.display = 'none';
        });
      });

      // Form submit
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        let isValid = true;

        inputs.forEach((input) => {
          if (!validateField(input)) {
            isValid = false;
          }
        });

        // Validate checkbox
        const checkbox = form.querySelector('input[type="checkbox"][required]');
        if (checkbox && !checkbox.checked) {
          isValid = false;
          const checkboxGroup = checkbox.closest('.checkbox-group');
          if (checkboxGroup) {
            checkboxGroup.style.border = '1px solid var(--danger)';
            checkboxGroup.style.borderRadius = '8px';
            checkboxGroup.style.padding = '8px';
          }
        }

        if (isValid) {
          // Show loading state
          const submitBtn = form.querySelector('button[type="submit"]');
          if (submitBtn) {
            setButtonLoading(submitBtn, 'Processing...');
          }

          // Simulate form submission
          setTimeout(() => {
            // Redirect to payment page (simulated)
            window.location.href = '/payment/1/';
          }, 1500);
        }
      });
    });
  }

  function validateField(input) {
    const rules = input.getAttribute('data-validate');
    if (!rules) return true;

    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';

    const rulesList = rules.split('|');

    for (const rule of rulesList) {
      if (rule === 'required' && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
        break;
      }

      if (rule.startsWith('min:')) {
        const min = parseInt(rule.split(':')[1], 10);
        if (value.length < min) {
          isValid = false;
          errorMessage = `Minimum ${min} characters required.`;
          break;
        }
      }

      if (rule === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          isValid = false;
          errorMessage = 'Please enter a valid email address.';
          break;
        }
      }

      if (rule === 'phone') {
        const phoneRegex = /^[+]?[\d\s-]{10,}$/;
        if (!phoneRegex.test(value)) {
          isValid = false;
          errorMessage = 'Please enter a valid phone number.';
          break;
        }
      }
    }

    // Toggle error state
    if (isValid) {
      input.classList.remove('error');
      input.classList.add('valid');
    } else {
      input.classList.add('error');
      input.classList.remove('valid');
    }

    // Show/hide error message
    let errorEl = input.parentNode.querySelector('.form-error');
    if (!errorEl) {
      errorEl = document.createElement('span');
      errorEl.className = 'form-error';
      input.parentNode.appendChild(errorEl);
    }

    if (!isValid) {
      errorEl.textContent = errorMessage;
      errorEl.style.display = 'block';
    } else {
      errorEl.style.display = 'none';
    }

    return isValid;
  }

  /* ==========================================
     IMAGE UPLOAD PREVIEW
     ========================================== */
  function initImagePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"][data-preview]');
    if (!fileInputs.length) return;

    fileInputs.forEach((input) => {
      const previewId = input.getAttribute('data-preview');
      const previewContainer = document.getElementById(previewId);
      if (!previewContainer) return;

      input.addEventListener('change', () => {
        const file = input.files[0];
        if (!file) {
          previewContainer.classList.remove('visible');
          previewContainer.innerHTML = '';
          return;
        }

        // Validate file type
        if (!file.type.startsWith('image/')) {
          alert('Please select a valid image file.');
          input.value = '';
          return;
        }

        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
          alert('File size must be less than 5MB.');
          input.value = '';
          return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
          previewContainer.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
          previewContainer.classList.add('visible');
        };
        reader.readAsDataURL(file);
      });
    });
  }

  /* ==========================================
     CONTACT FORM HANDLING
     ========================================== */
  function initContactForm() {
    const contactForm = document.querySelector('.contact-form');
    if (!contactForm) return;

    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const submitBtn = contactForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        setButtonLoading(submitBtn, 'Sending...');
      }

      // Simulate form submission
      setTimeout(() => {
        if (submitBtn) {
          resetButton(submitBtn);
        }

        // Show success message
        const successMsg = contactForm.querySelector('.form-success-message');
        if (successMsg) {
          successMsg.style.display = 'block';
        }

        contactForm.reset();
      }, 1500);
    });
  }

  /* ==========================================
     PAYMENT BUTTON HANDLERS
     ========================================== */
  function initPaymentButtons() {
    const paystackBtn = document.querySelector('[data-payment="paystack"]');
    const flutterwaveBtn = document.querySelector('[data-payment="flutterwave"]');

    if (paystackBtn) {
      paystackBtn.addEventListener('click', function () {
        setButtonLoading(this, 'Redirecting...');

        // Simulate Paystack redirect
        setTimeout(() => {
          // In production, this would redirect to Paystack
          window.location.href = '/payment/success/';
        }, 1500);
      });
    }

    if (flutterwaveBtn) {
      flutterwaveBtn.addEventListener('click', function () {
        setButtonLoading(this, 'Redirecting...');

        // Simulate Flutterwave redirect
        setTimeout(() => {
          // In production, this would redirect to Flutterwave
          window.location.href = '/payment/success/';
        }, 1500);
      });
    }
  }

  /* ==========================================
     NEWSLETTER FORM
     ========================================== */
  function initNewsletterForm() {
    const form = document.querySelector('.newsletter-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      const btn = form.querySelector('button');

      if (!input.value.trim()) {
        input.style.borderColor = 'var(--danger)';
        return;
      }

      const originalText = btn.textContent;
      btn.textContent = 'Subscribed!';
      btn.style.background = 'var(--success)';
      input.value = '';

      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
      }, 3000);
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
     DOWNLOAD RECEIPT
     ========================================== */
  function initDownloadReceipt() {
    const downloadBtn = document.querySelector('[data-action="download-receipt"]');
    if (!downloadBtn) return;

    downloadBtn.addEventListener('click', (e) => {
      e.preventDefault();

      setButtonLoading(downloadBtn, 'Generating...');

      setTimeout(() => {
        resetButton(downloadBtn);

        // Create a simple receipt as text download
        const receiptText = `
KOHI DOJO CANTABALL LEAGUE
==========================

Payment Receipt
Reference: KDCBL-2025-W5-0018
Date: ${new Date().toLocaleDateString()}

Team: Team Alpha
Week: Week 5
Date: January 25, 2025

Amount Paid: N5,000.00
Payment Method: Paystack
Status: PAID

Thank you for registering!
        `.trim();

        const blob = new Blob([receiptText], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'receipt-KDCBL-2025-W5-0018.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 1000);
    });
  }

  /* ==========================================
     INITIALIZE
     ========================================== */
  function init() {
    initFormValidation();
    initImagePreview();
    initContactForm();
    initPaymentButtons();
    initNewsletterForm();
    initDownloadReceipt();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
