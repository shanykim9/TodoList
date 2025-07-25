/**
 * Todo List Application JavaScript
 * Provides enhanced user experience and client-side functionality
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    setupFormValidation();
    setupKeyboardShortcuts();
    setupAutoFocus();
    setupSmoothAnimations();
    setupFormSubmissionHandling();
    
    console.log('Todo App initialized successfully');
}

/**
 * Setup form validation for better UX
 */
function setupFormValidation() {
    const addForm = document.getElementById('addTodoForm');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            const titleInput = document.getElementById('title');
            const title = titleInput.value.trim();
            
            // Client-side validation
            if (!title) {
                e.preventDefault();
                showValidationError(titleInput, 'Task title is required!');
                return false;
            }
            
            if (title.length > 200) {
                e.preventDefault();
                showValidationError(titleInput, 'Task title must be less than 200 characters!');
                return false;
            }
            
            // Show loading state
            showFormLoading(this);
        });
        
        // Real-time character counter
        const titleInput = document.getElementById('title');
        if (titleInput) {
            setupCharacterCounter(titleInput, 200);
        }
    }
    
    // Setup validation for edit forms
    setupEditFormValidation();
}

/**
 * Setup validation for edit forms in modals
 */
function setupEditFormValidation() {
    const editModals = document.querySelectorAll('[id^="editModal"]');
    editModals.forEach(modal => {
        const form = modal.querySelector('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                const titleInput = form.querySelector('input[name="title"]');
                const title = titleInput.value.trim();
                
                if (!title) {
                    e.preventDefault();
                    showValidationError(titleInput, 'Task title is required!');
                    return false;
                }
                
                if (title.length > 200) {
                    e.preventDefault();
                    showValidationError(titleInput, 'Task title must be less than 200 characters!');
                    return false;
                }
                
                showFormLoading(this);
            });
            
            // Setup character counter for edit forms
            const titleInput = form.querySelector('input[name="title"]');
            if (titleInput) {
                setupCharacterCounter(titleInput, 200);
            }
        }
    });
}

/**
 * Setup character counter for input fields
 */
function setupCharacterCounter(input, maxLength) {
    // Create counter element
    const counter = document.createElement('div');
    counter.className = 'form-text character-counter';
    counter.style.textAlign = 'right';
    
    // Insert counter after the input
    input.parentNode.appendChild(counter);
    
    // Update counter function
    function updateCounter() {
        const length = input.value.length;
        const remaining = maxLength - length;
        counter.textContent = `${length}/${maxLength} characters`;
        
        if (remaining < 20) {
            counter.className = 'form-text character-counter text-warning';
        } else if (remaining < 0) {
            counter.className = 'form-text character-counter text-danger';
        } else {
            counter.className = 'form-text character-counter text-muted';
        }
    }
    
    // Initial update and event listeners
    updateCounter();
    input.addEventListener('input', updateCounter);
    input.addEventListener('paste', () => setTimeout(updateCounter, 10));
}

/**
 * Show validation error for input field
 */
function showValidationError(input, message) {
    // Remove existing error
    const existingError = input.parentNode.querySelector('.validation-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error class to input
    input.classList.add('is-invalid');
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback validation-error';
    errorDiv.textContent = message;
    
    // Insert error message
    input.parentNode.appendChild(errorDiv);
    
    // Focus on the input
    input.focus();
    
    // Remove error after user starts typing
    input.addEventListener('input', function removeError() {
        input.classList.remove('is-invalid');
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
        input.removeEventListener('input', removeError);
    }, { once: true });
}

/**
 * Show loading state for forms
 */
function showFormLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        submitBtn.disabled = true;
        
        // Store original text for potential restoration
        submitBtn.dataset.originalText = originalText;
    }
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit form
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                activeForm.requestSubmit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modalInstance = bootstrap.Modal.getInstance(openModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
        
        // Focus on add task input with 'n' key
        if (e.key === 'n' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            const activeElement = document.activeElement;
            if (activeElement.tagName !== 'INPUT' && activeElement.tagName !== 'TEXTAREA') {
                e.preventDefault();
                const titleInput = document.getElementById('title');
                if (titleInput) {
                    titleInput.focus();
                }
            }
        }
    });
}

/**
 * Setup auto-focus functionality
 */
function setupAutoFocus() {
    // Auto-focus on the first input when page loads
    const titleInput = document.getElementById('title');
    if (titleInput && !isMobileDevice()) {
        // Small delay to ensure page is fully rendered
        setTimeout(() => {
            titleInput.focus();
        }, 100);
    }
    
    // Auto-focus on edit modal inputs when they open
    const editModals = document.querySelectorAll('[id^="editModal"]');
    editModals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const titleInput = modal.querySelector('input[name="title"]');
            if (titleInput) {
                titleInput.focus();
                titleInput.select(); // Select all text for easy editing
            }
        });
    });
}

/**
 * Check if device is mobile
 */
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Setup smooth animations and transitions
 */
function setupSmoothAnimations() {
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Animate alert dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto-dismiss success messages after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                const alertInstance = bootstrap.Alert.getInstance(alert);
                if (alertInstance) {
                    alertInstance.close();
                }
            }, 5000);
        }
    });
    
    // Animate todo item interactions
    setupTodoItemAnimations();
}

/**
 * Setup animations for todo items
 */
function setupTodoItemAnimations() {
    const todoItems = document.querySelectorAll('.todo-item');
    
    todoItems.forEach(item => {
        // Add hover effects
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateX(0)';
        });
    });
    
    // Animate checkbox changes
    const checkboxes = document.querySelectorAll('.todo-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('click', function(e) {
            // Add a small animation to the checkbox
            this.style.transform = 'scale(0.8)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
}

/**
 * Setup form submission handling with better UX
 */
function setupFormSubmissionHandling() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Disable multiple submissions
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                setTimeout(() => {
                    submitBtn.disabled = true;
                }, 50);
            }
        });
    });
}

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

/**
 * Handle network errors gracefully
 */
window.addEventListener('online', function() {
    showToast('Connection restored!', 'success');
});

window.addEventListener('offline', function() {
    showToast('You are offline. Some features may not work.', 'warning');
});

/**
 * Handle form submission errors
 */
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showToast('An error occurred. Please try again.', 'danger');
});
