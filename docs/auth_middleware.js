// Authentication Middleware
// This script should be included on all protected pages

import { requireAuth, onAuthStateChange, getCurrentUser, isDevelopment } from './auth.js';

// Authentication check function
function checkAuthentication() {
    // In development mode, always allow access
    if (isDevelopment) {
        console.log('🚀 Development mode: Authentication check bypassed');
        showProtectedContent();
        return;
    }
    
    // Check if user is authenticated
    if (!requireAuth()) {
        return; // Redirect will happen automatically
    }
    
    // User is authenticated, show protected content
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

// Add authentication UI elements to protected pages
function addAuthUI() {
    // Find the site toolbar to add auth elements
    const siteToolbar = document.querySelector('.site-toolbar');
    if (!siteToolbar) return;
    
    // Create auth section
    const authSection = document.createElement('div');
    authSection.className = 'auth-section';
    authSection.style.cssText = `
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-left: auto;
    `;
    
    // Add user info
    const userInfo = document.createElement('div');
    userInfo.className = 'user-info';
    userInfo.setAttribute('data-auth', 'user-info');
    userInfo.style.cssText = `
        display: none;
        align-items: center;
        gap: 0.5rem;
        color: white;
        font-size: 0.9rem;
    `;
    
    const userAvatar = document.createElement('img');
    userAvatar.className = 'user-avatar';
    userAvatar.setAttribute('data-user-info', 'avatar');
    userAvatar.style.cssText = `
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.3);
    `;
    
    const userName = document.createElement('span');
    userName.className = 'user-name';
    userName.setAttribute('data-user-info', 'name');
    userName.style.cssText = `
        font-weight: 500;
    `;
    
    userInfo.appendChild(userAvatar);
    userInfo.appendChild(userName);
    
    // Add sign out button
    const signOutBtn = document.createElement('button');
    signOutBtn.className = 'sign-out-btn';
    signOutBtn.setAttribute('data-auth', 'sign-out');
    signOutBtn.textContent = isDevelopment ? 'Sign Out (DEV)' : 'Sign Out';
    signOutBtn.style.cssText = `
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s ease;
    `;
    
    signOutBtn.addEventListener('mouseenter', () => {
        signOutBtn.style.background = 'rgba(255, 255, 255, 0.2)';
        signOutBtn.style.borderColor = 'rgba(255, 255, 255, 0.5)';
    });
    
    signOutBtn.addEventListener('mouseleave', () => {
        signOutBtn.style.background = 'rgba(255, 255, 255, 0.1)';
        signOutBtn.style.borderColor = 'rgba(255, 255, 255, 0.3)';
    });
    
    signOutBtn.addEventListener('click', async () => {
        try {
            const { signOutUser } = await import('./auth.js');
            await signOutUser();
        } catch (error) {
            console.error('Sign out error:', error);
        }
    });
    
    // Add elements to auth section
    authSection.appendChild(userInfo);
    authSection.appendChild(signOutBtn);
    
    // Add auth section to toolbar
    siteToolbar.appendChild(authSection);
}

// Add loading state to protected content
function addLoadingStates() {
    // Skip loading states in development
    if (isDevelopment) {
        console.log('🚀 Development mode: Loading states skipped');
        return;
    }
    
    // Add loading class to main content
    const mainContent = document.querySelector('.container');
    if (mainContent) {
        mainContent.classList.add('auth-loading');
    }
    
    // Add loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'auth-loading-overlay';
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(10px);
    `;
    
    const loadingContent = document.createElement('div');
    loadingContent.style.cssText = `
        text-align: center;
        color: #4a5568;
    `;
    
    const spinner = document.createElement('div');
    spinner.style.cssText = `
        width: 40px;
        height: 40px;
        border: 4px solid #e2e8f0;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    `;
    
    const loadingText = document.createElement('div');
    loadingText.textContent = 'Verifying authentication...';
    loadingText.style.cssText = `
        font-size: 1.1rem;
        font-weight: 500;
    `;
    
    loadingContent.appendChild(spinner);
    loadingContent.appendChild(loadingText);
    loadingOverlay.appendChild(loadingContent);
    
    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(loadingOverlay);
    
    // Remove loading overlay when auth is complete
    onAuthStateChange((user) => {
        if (user) {
            loadingOverlay.style.display = 'none';
        }
    });
}

// Initialize authentication middleware
function initAuthMiddleware() {
    console.log(`🔐 Initializing auth middleware in ${isDevelopment ? 'development' : 'production'} mode`);
    
    // In development mode, immediately show content and skip auth checks
    if (isDevelopment) {
        console.log('🚀 Development mode: Bypassing all authentication checks');
        showProtectedContent();
        addAuthUI();
        return;
    }
    
    // Production mode - add loading states first
    addLoadingStates();
    
    // Add auth UI elements
    addAuthUI();
    
    // Wait for Firebase auth to initialize before checking authentication
    console.log('⏳ Waiting for Firebase auth to initialize...');
    setTimeout(() => {
        console.log('🔍 Checking authentication after Firebase init...');
        checkAuthentication();
    }, 2000); // Wait 2 seconds for Firebase to fully initialize
    
    // Listen for auth state changes
    onAuthStateChange((user) => {
        if (user) {
            showProtectedContent();
        } else {
            // User signed out, redirect to login
            // Use absolute URL in production, relative in development
            const loginUrl = isDevelopment 
                ? '/login.html'
                : 'https://davodey.github.io/folklife-scrape-site/login.html';
            window.location.href = loginUrl;
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuthMiddleware);
} else {
    initAuthMiddleware();
}

// Export functions for use in other scripts
export { checkAuthentication, showProtectedContent, updateUserInfo };
