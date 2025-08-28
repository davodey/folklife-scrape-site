// Authentication Middleware
// This script handles UI updates for protected pages

import { requireAuth, onAuthStateChange, getCurrentUser } from './auth.js';

// Environment detection
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1' || 
                     window.location.hostname.includes('localhost');

// Authentication check function - simplified to avoid conflicts
function checkAuthentication() {
    // Just show protected content if we're here
    // The main auth.js will handle the actual authentication
    showProtectedContent();
}

// Show protected content
function showProtectedContent() {
    // Remove any loading states
    const loadingElements = document.querySelectorAll('.auth-loading');
    loadingElements.forEach(el => el.style.display = 'none');
    
    // Show protected content
    const protectedElements = document.querySelectorAll('.protected-content');
    protectedElements.forEach(el => el.style.display = 'block');
    
    // Update user info in the UI
    updateUserInfo();
}

// Update user information in the UI
function updateUserInfo() {
    const user = getCurrentUser();
    if (!user) return;
    
    // Update user info elements
    const userInfoElements = document.querySelectorAll('[data-user-info]');
    userInfoElements.forEach(element => {
        const infoType = element.dataset.userInfo;
        
        switch (infoType) {
            case 'name':
                element.textContent = user.displayName || user.email;
                break;
            case 'email':
                element.textContent = user.email;
                break;
            case 'avatar':
                if (user.photoURL) {
                    element.src = user.photoURL;
                    element.style.display = 'block';
                } else {
                    element.style.display = 'none';
                }
                break;
        }
    });
}

// Initialize the middleware
function initMiddleware() {
    console.log('🔧 Initializing auth middleware...');
    
    // Wait for auth to be ready, then check authentication
    onAuthStateChange((user) => {
        if (user) {
            console.log('✅ Auth middleware: User authenticated, showing content');
            checkAuthentication();
        } else {
            console.log('❌ Auth middleware: No user, redirecting');
            // Let auth.js handle the redirect
        }
    });
}

// Start the middleware
initMiddleware();
