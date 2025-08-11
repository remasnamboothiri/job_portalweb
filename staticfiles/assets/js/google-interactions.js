// Google-style interactions and utilities
class GoogleInteractions {
  constructor() {
    this.init();
  }

  init() {
    this.setupSearchFunctionality();
    this.setupFormValidation();
    this.setupLoadingStates();
    this.setupModalHandlers();
    this.setupDropdownHandlers();
  }

  // Instant search functionality
  setupSearchFunctionality() {
    const searchInputs = document.querySelectorAll('.search-bar input, .input-google[data-search]');
    
    searchInputs.forEach(input => {
      let searchTimeout;
      
      input.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length > 2) {
          searchTimeout = setTimeout(() => {
            this.performSearch(query, input);
          }, 300);
        }
      });
    });
  }

  performSearch(query, inputElement) {
    const resultsContainer = inputElement.getAttribute('data-results') || 
                           document.querySelector('.search-results');
    
    if (!resultsContainer) return;

    // Show loading state
    this.showSearchLoading(resultsContainer);
    
    // Simulate API call
    setTimeout(() => {
      this.displaySearchResults(query, resultsContainer);
    }, 500);
  }

  showSearchLoading(container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    
    if (container) {
      container.innerHTML = `
        <div class="flex flex-center p-32">
          <div class="spinner-google"></div>
          <span class="ml-16">Searching...</span>
        </div>
      `;
    }
  }

  displaySearchResults(query, container) {
    if (typeof container === 'string') {
      container = document.querySelector(container);
    }
    
    // Mock search results
    const mockResults = [
      { title: 'Senior Frontend Developer', company: 'Google', location: 'Mountain View, CA' },
      { title: 'React Developer', company: 'Meta', location: 'Menlo Park, CA' },
      { title: 'Full Stack Engineer', company: 'Netflix', location: 'Los Gatos, CA' }
    ];

    const resultsHTML = mockResults.map(result => `
      <div class="card-google card-google-compact mb-16">
        <h4>${result.title}</h4>
        <p class="text-muted">${result.company} • ${result.location}</p>
      </div>
    `).join('');

    if (container) {
      container.innerHTML = resultsHTML;
    }
  }

  // Form validation with clean feedback
  setupFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
      form.addEventListener('submit', (e) => {
        if (!this.validateForm(form)) {
          e.preventDefault();
        }
      });

      // Real-time validation
      const inputs = form.querySelectorAll('.input-google');
      inputs.forEach(input => {
        input.addEventListener('blur', () => {
          this.validateField(input);
        });
      });
    });
  }

  validateForm(form) {
    const inputs = form.querySelectorAll('.input-google[required]');
    let isValid = true;

    inputs.forEach(input => {
      if (!this.validateField(input)) {
        isValid = false;
      }
    });

    return isValid;
  }

  validateField(input) {
    const value = input.value.trim();
    const type = input.type;
    let isValid = true;
    let message = '';

    // Remove existing error
    this.clearFieldError(input);

    if (input.hasAttribute('required') && !value) {
      isValid = false;
      message = 'This field is required';
    } else if (type === 'email' && value && !this.isValidEmail(value)) {
      isValid = false;
      message = 'Please enter a valid email address';
    }

    if (!isValid) {
      this.showFieldError(input, message);
    }

    return isValid;
  }

  showFieldError(input, message) {
    input.style.borderColor = 'var(--google-red)';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.cssText = `
      color: var(--google-red);
      font-size: 12px;
      margin-top: 4px;
    `;
    errorDiv.textContent = message;
    
    input.parentNode.appendChild(errorDiv);
  }

  clearFieldError(input) {
    input.style.borderColor = '';
    const existingError = input.parentNode.querySelector('.field-error');
    if (existingError) {
      existingError.remove();
    }
  }

  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  // Loading states with Google-style spinners
  setupLoadingStates() {
    document.addEventListener('click', (e) => {
      const button = e.target.closest('.btn-google[data-loading]');
      if (button) {
        this.showButtonLoading(button);
      }
    });
  }

  showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.innerHTML = `
      <div class="spinner-google"></div>
      <span>Loading...</span>
    `;
    button.disabled = true;

    // Restore after 2 seconds (or when your actual operation completes)
    setTimeout(() => {
      button.innerHTML = originalText;
      button.disabled = false;
    }, 2000);
  }

  // Modal handlers
  setupModalHandlers() {
    // Open modal
    document.addEventListener('click', (e) => {
      const trigger = e.target.closest('[data-modal]');
      if (trigger) {
        const modalId = trigger.getAttribute('data-modal');
        this.openModal(modalId);
      }
    });

    // Close modal
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-google')) {
        this.closeModal(e.target);
      }
      
      const closeBtn = e.target.closest('.modal-close');
      if (closeBtn) {
        const modal = closeBtn.closest('.modal-google');
        this.closeModal(modal);
      }
    });

    // ESC key to close modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal-google[style*="block"]');
        if (openModal) {
          this.closeModal(openModal);
        }
      }
    });
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'block';
      document.body.style.overflow = 'hidden';
    }
  }

  closeModal(modal) {
    if (typeof modal === 'string') {
      modal = document.getElementById(modal);
    }
    
    if (modal) {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  // Dropdown handlers
  setupDropdownHandlers() {
    document.addEventListener('click', (e) => {
      // Close all dropdowns when clicking outside
      if (!e.target.closest('.dropdown-google')) {
        const openDropdowns = document.querySelectorAll('.dropdown-google-content[style*="block"]');
        openDropdowns.forEach(dropdown => {
          dropdown.style.display = 'none';
        });
      }
    });
  }

  // Utility methods
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  // Smooth page transitions
  setupPageTransitions() {
    const links = document.querySelectorAll('a[data-transition]');
    
    links.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const href = link.href;
        
        // Fade out current page
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.3s ease';
        
        setTimeout(() => {
          window.location.href = href;
        }, 300);
      });
    });
  }

  // Initialize page fade in
  initPageFadeIn() {
    document.body.style.opacity = '0';
    window.addEventListener('load', () => {
      document.body.style.transition = 'opacity 0.3s ease';
      document.body.style.opacity = '1';
    });
  }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new GoogleInteractions();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GoogleInteractions;
}