// Premium Interactions & Micro-animations
class PremiumInteractions {
  constructor() {
    this.init();
  }

  init() {
    this.setupMagneticButtons();
    this.setupParallaxScroll();
    this.setupIntersectionObserver();
    this.setupRippleEffect();
    this.setupToastNotifications();
    this.setupProgressAnimations();
    this.setupSkeletonLoading();
    this.setupFloatingLabels();
  }

  // Magnetic button effect
  setupMagneticButtons() {
    const magneticElements = document.querySelectorAll('.magnetic-premium');
    
    magneticElements.forEach(element => {
      element.addEventListener('mousemove', (e) => {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        element.style.transform = `translate(${x * 0.1}px, ${y * 0.1}px)`;
      });
      
      element.addEventListener('mouseleave', () => {
        element.style.transform = 'translate(0, 0)';
      });
    });
  }

  // Parallax scroll effect
  setupParallaxScroll() {
    const parallaxElements = document.querySelectorAll('.parallax-premium');
    
    window.addEventListener('scroll', this.throttle(() => {
      const scrolled = window.pageYOffset;
      
      parallaxElements.forEach(element => {
        const rate = scrolled * -0.5;
        element.style.transform = `translateY(${rate}px)`;
      });
    }, 16));
  }

  // Intersection Observer for animations
  setupIntersectionObserver() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          
          // Stagger animation for children
          if (entry.target.classList.contains('stagger-premium')) {
            this.animateStagger(entry.target);
          }
        }
      });
    }, observerOptions);

    // Observe elements
    const animateElements = document.querySelectorAll(
      '.slide-in-left, .slide-in-right, .slide-in-up, .stagger-premium'
    );
    
    animateElements.forEach(el => observer.observe(el));
  }

  // Stagger animation for lists
  animateStagger(container) {
    const children = container.children;
    Array.from(children).forEach((child, index) => {
      setTimeout(() => {
        child.style.opacity = '1';
        child.style.transform = 'translateY(0)';
      }, index * 100);
    });
  }

  // Ripple effect for buttons
  setupRippleEffect() {
    document.addEventListener('click', (e) => {
      const button = e.target.closest('.btn-premium, .fab-premium');
      if (!button) return;

      const ripple = document.createElement('span');
      const rect = button.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;

      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        left: ${x}px;
        top: ${y}px;
        width: ${size}px;
        height: ${size}px;
        pointer-events: none;
      `;

      button.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 600);
    });

    // Add ripple keyframes
    if (!document.querySelector('#ripple-styles')) {
      const style = document.createElement('style');
      style.id = 'ripple-styles';
      style.textContent = `
        @keyframes ripple {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }

  // Toast notifications
  setupToastNotifications() {
    window.showToast = (message, type = 'success') => {
      const toast = document.createElement('div');
      toast.className = `toast-premium ${type}`;
      toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
          <span>${this.getToastIcon(type)}</span>
          <span>${message}</span>
          <button onclick="this.parentElement.parentElement.remove()" 
                  style="background: none; border: none; font-size: 18px; cursor: pointer; margin-left: auto;">×</button>
        </div>
      `;

      document.body.appendChild(toast);
      
      // Show toast
      setTimeout(() => toast.classList.add('show'), 100);
      
      // Auto remove after 4 seconds
      setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
      }, 4000);
    };
  }

  getToastIcon(type) {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️'
    };
    return icons[type] || icons.info;
  }

  // Progress bar animations
  setupProgressAnimations() {
    const progressBars = document.querySelectorAll('.progress-premium-bar');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const bar = entry.target;
          const targetWidth = bar.getAttribute('data-width') || '75%';
          
          setTimeout(() => {
            bar.style.width = targetWidth;
          }, 200);
        }
      });
    });

    progressBars.forEach(bar => observer.observe(bar));
  }

  // Skeleton loading
  setupSkeletonLoading() {
    window.showSkeleton = (container, count = 3) => {
      const skeletonHTML = Array(count).fill().map(() => `
        <div class="skeleton-premium skeleton-text"></div>
      `).join('');
      
      if (typeof container === 'string') {
        container = document.querySelector(container);
      }
      
      if (container) {
        container.innerHTML = skeletonHTML;
      }
    };

    window.hideSkeleton = (container, content) => {
      if (typeof container === 'string') {
        container = document.querySelector(container);
      }
      
      if (container) {
        container.innerHTML = content;
      }
    };
  }

  // Floating labels
  setupFloatingLabels() {
    const inputs = document.querySelectorAll('.input-premium input');
    
    inputs.forEach(input => {
      // Set placeholder for CSS selector
      if (!input.placeholder) {
        input.placeholder = ' ';
      }
      
      // Handle autofill
      input.addEventListener('animationstart', (e) => {
        if (e.animationName === 'onAutoFillStart') {
          input.classList.add('has-value');
        }
      });
    });
  }

  // Smooth scroll to element
  smoothScrollTo(element, offset = 0) {
    const targetElement = typeof element === 'string' 
      ? document.querySelector(element) 
      : element;
    
    if (targetElement) {
      const targetPosition = targetElement.offsetTop - offset;
      
      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });
    }
  }

  // Animate counter
  animateCounter(element, start = 0, end = 100, duration = 2000) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
      current += increment;
      element.textContent = Math.floor(current);
      
      if (current >= end) {
        element.textContent = end;
        clearInterval(timer);
      }
    }, 16);
  }

  // Typewriter effect
  typeWriter(element, text, speed = 50) {
    element.textContent = '';
    let i = 0;
    
    const timer = setInterval(() => {
      element.textContent += text.charAt(i);
      i++;
      
      if (i >= text.length) {
        clearInterval(timer);
      }
    }, speed);
  }

  // Utility: Throttle function
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

  // Utility: Debounce function
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

  // Page transition effect
  pageTransition(url) {
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(0.95)';
    document.body.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    
    setTimeout(() => {
      window.location.href = url;
    }, 300);
  }

  // Initialize page entrance animation
  initPageEntrance() {
    document.body.style.opacity = '0';
    document.body.style.transform = 'scale(0.95)';
    
    window.addEventListener('load', () => {
      document.body.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
      document.body.style.opacity = '1';
      document.body.style.transform = 'scale(1)';
    });
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  window.premiumUI = new PremiumInteractions();
  
  // Initialize page entrance
  window.premiumUI.initPageEntrance();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PremiumInteractions;
}