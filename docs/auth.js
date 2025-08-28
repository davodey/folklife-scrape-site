// Firebase Authentication Module
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { 
    getAuth, 
    signInWithPopup, 
    GoogleAuthProvider, 
    OAuthProvider,
    signOut,
    onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js";

// Environment detection
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1' || 
                     window.location.hostname.includes('localhost');

const isProduction = !isDevelopment;

console.log(`🔍 Environment detected: ${isDevelopment ? 'Development' : 'Production'}`);
console.log(`🔍 Hostname: ${window.location.hostname}`);
console.log(`🔍 Pathname: ${window.location.pathname}`);
console.log(`🔍 Full URL: ${window.location.href}`);

// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyCdOH2K3N79pb76zg6MTUK293Z3Rg-0tjQ",
    authDomain: "folklife-e6f03.firebaseapp.com",
    projectId: "folklife-e6f03",
    storageBucket: "folklife-e6f03.firebasestorage.app",
    messagingSenderId: "28797119827",
    appId: "1:28797119827:web:13996317828a6f04f845a6",
    measurementId: "G-XLGSBBM5RD"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);

// Auth providers
const googleProvider = new GoogleAuthProvider();
const microsoftProvider = new OAuthProvider('microsoft.com');

// User state
let currentUser = null;
let authStateListeners = [];

// Initialize authentication
export function initAuth() {
    console.log('🔐 ===== AUTHENTICATION INITIALIZATION START =====');
    console.log('🔐 Initializing authentication...');
    console.log('🌐 Current domain:', window.location.hostname);
    console.log('🔗 Current URL:', window.location.href);
    console.log('📍 Current pathname:', window.location.pathname);
    console.log('📄 Document ready state:', document.readyState);
    console.log('🔍 Environment detected:', isDevelopment ? 'Development' : 'Production');
    
    if (isDevelopment) {
        console.log('🚀 Development mode: Authentication bypassed');
        // In development, simulate authenticated user
        currentUser = {
            uid: 'dev-user',
            email: 'developer@localhost',
            displayName: 'Local Developer',
            photoURL: null
        };
        console.log('🚀 Development: Setting simulated user:', currentUser);
        updateUIForAuthState(currentUser);
        notifyAuthStateListeners(currentUser);
        console.log('🔐 ===== AUTHENTICATION INITIALIZATION COMPLETE (DEV MODE) =====');
        return;
    }

    console.log('🔐 Production mode: Firebase authentication enabled');
    
    // Check if we're on an authorized domain
    const currentDomain = window.location.hostname;
    if (currentDomain === 'davodey.github.io') {
        console.log('✅ Domain check: GitHub Pages domain detected');
    } else {
        console.log('⚠️ Domain check: Unexpected domain:', currentDomain);
    }
    
    // Initialize UI state immediately
    console.log('🎨 Initializing UI state immediately...');
    updateUIForAuthState(null);
    
    console.log('🔄 Setting up Firebase auth state listener...');
    onAuthStateChanged(auth, (user) => {
        console.log('🔄 ===== AUTH STATE CHANGED =====');
        console.log('🔄 Auth state changed:', user ? `User: ${user.email}` : 'No user');
        console.log('🔄 Previous user:', currentUser);
        console.log('🔄 New user:', user);
        
        currentUser = user;
        console.log('🔄 Current user updated to:', currentUser);
        
        console.log('🎨 Calling updateUIForAuthState...');
        updateUIForAuthState(user);
        
        console.log('🔔 Notifying auth state listeners...');
        notifyAuthStateListeners(user);
        
        if (user) {
            console.log('✅ ===== USER AUTHENTICATED =====');
            console.log('✅ User signed in:', user.email);
            console.log('📍 Current pathname:', window.location.pathname);
            console.log('📍 Current href:', window.location.href);
            
            // Check email domain before allowing access
            const userEmail = user.email;
            const allowedDomains = ['@si.edu', '@quotient-inc.com'];
            const hasAllowedDomain = allowedDomains.some(domain => userEmail.endsWith(domain));
            
            console.log('🔍 Email domain validation:', {
                userEmail: userEmail,
                allowedDomains: allowedDomains,
                hasAllowedDomain: hasAllowedDomain
            });
            
            if (!hasAllowedDomain) {
                console.log('🚫 User email domain not allowed:', userEmail);
                console.log('🚫 Signing out unauthorized user');
                
                // Sign out the unauthorized user
                signOut(auth).then(() => {
                    console.log('🚫 Unauthorized user signed out');
                    // Show error message to user
                    showDomainError();
                }).catch(error => {
                    console.error('❌ Error signing out unauthorized user:', error);
                });
                return;
            }
            
            console.log('✅ Email domain validation passed');
            
            // Check if we're on a login page (more flexible check for GitHub Pages)
            const isOnLoginPage = window.location.href.includes('login.html') || 
                                window.location.pathname.includes('login.html') ||
                                window.location.pathname.endsWith('/') ||
                                window.location.pathname === '/folklife-scrape-site/';
            
            console.log('🔍 Login page check:', {
                hrefIncludesLogin: window.location.href.includes('login.html'),
                pathnameIncludesLogin: window.location.pathname.includes('login.html'),
                pathnameEndsWithSlash: window.location.pathname.endsWith('/'),
                pathnameIsBase: window.location.pathname === '/folklife-scrape-site/',
                isOnLoginPage: isOnLoginPage
            });
            
            if (isOnLoginPage) {
                // For GitHub Pages, use the correct base path
                const basePath = '/folklife-scrape-site';
                const redirectPath = basePath + '/index.html';
                console.log('🔄 Redirecting authenticated user to:', redirectPath);
                
                // Use a small delay to ensure the auth state is fully processed
                setTimeout(() => {
                    console.log('🚀 Executing redirect to:', redirectPath);
                    window.location.href = redirectPath;
                }, 500); // Increased delay for reliability
            } else {
                console.log('📍 User is authenticated but not on login page, no redirect needed');
            }
        } else {
            console.log('❌ ===== USER NOT AUTHENTICATED =====');
            console.log('❌ User signed out');
            console.log('📍 Current pathname:', window.location.pathname);
            console.log('📍 Current href:', window.location.href);
            
            // Check if we're NOT on a login page (more flexible check)
            const isOnLoginPage = window.location.href.includes('login.html') || 
                                window.location.pathname.includes('login.html');
            
            console.log('🔍 Login page check for redirect:', {
                hrefIncludesLogin: window.location.href.includes('login.html'),
                pathnameIncludesLogin: window.location.pathname.includes('login.html'),
                isOnLoginPage: isOnLoginPage
            });
            
            if (!isOnLoginPage) {
                const basePath = '/folklife-scrape-site';
                const loginPath = basePath + '/login.html';
                console.log('🔄 Redirecting unauthenticated user to:', loginPath);
                window.location.href = loginPath;
            } else {
                console.log('📍 User is not authenticated but already on login page, no redirect needed');
            }
        }
        console.log('🔄 ===== AUTH STATE CHANGE COMPLETE =====');
    });
    
    console.log('🔐 ===== AUTHENTICATION INITIALIZATION COMPLETE (PROD MODE) =====');
}

// Sign in with Google
export async function signInWithGoogle() {
    if (isDevelopment) {
        console.log('🚀 Development mode: Google sign-in simulated');
        return { user: currentUser };
    }

    try {
        console.log('🔐 Attempting Google sign-in...');
        const result = await signInWithPopup(auth, googleProvider);
        console.log('✅ Google sign-in successful:', result.user.email);
        return result.user;
    } catch (error) {
        console.error('❌ Google sign-in error:', error);
        
        // Handle specific error cases
        if (error.code === 'auth/unauthorized-domain') {
            console.error('🚫 Domain not authorized. Please add this domain to Firebase authorized domains.');
            throw new Error('This domain is not authorized for authentication. Please contact support.');
        } else if (error.code === 'auth/popup-blocked') {
            console.error('🚫 Popup blocked by browser. Please allow popups for this site.');
            throw new Error('Authentication popup was blocked. Please allow popups and try again.');
        } else if (error.code === 'auth/popup-closed-by-user') {
            console.error('🚫 Popup closed by user.');
            throw new Error('Authentication was cancelled. Please try again.');
        }
        
        throw error;
    }
}

// Sign in with Microsoft
export async function signInWithMicrosoft() {
    if (isDevelopment) {
        console.log('🚀 Development mode: Microsoft sign-in simulated');
        return { user: currentUser };
    }

    try {
        console.log('🔐 Attempting Microsoft sign-in...');
        const result = await signInWithPopup(auth, microsoftProvider);
        console.log('✅ Microsoft sign-in successful:', result.user.email);
        return result.user;
    } catch (error) {
        console.error('❌ Microsoft sign-in error:', error);
        
        // Handle specific error cases
        if (error.code === 'auth/unauthorized-domain') {
            console.error('🚫 Domain not authorized. Please add this domain to Firebase authorized domains.');
            throw new Error('This domain is not authorized for authentication. Please contact support.');
        } else if (error.code === 'auth/popup-blocked') {
            console.error('🚫 Popup blocked by browser. Please allow popups for this site.');
            throw new Error('Authentication popup was blocked. Please allow popups and try again.');
        } else if (error.code === 'auth/popup-closed-by-user') {
            console.error('🚫 Popup closed by user.');
            throw new Error('Authentication was cancelled. Please try again.');
        }
        
        throw error;
    }
}

// Sign out user
export async function signOutUser() {
    if (isDevelopment) {
        console.log('🚀 Development mode: Sign-out simulated');
        currentUser = null;
        updateUIForAuthState(null);
        notifyAuthStateListeners(null);
        return;
    }

    try {
        await signOut(auth);
        const basePath = '/folklife-scrape-site';
        const loginPath = basePath + '/login.html';
        console.log('Redirecting signed out user to:', loginPath);
        window.location.href = loginPath;
    } catch (error) {
        console.error('Sign-out error:', error);
        throw error;
    }
}

// Get current user
export function getCurrentUser() {
    return currentUser;
}

// Check if user is authenticated
export function isAuthenticated() {
    console.log('🔐 ===== AUTHENTICATION CHECK =====');
    console.log('🔐 Environment:', isDevelopment ? 'Development' : 'Production');
    console.log('🔐 Current user:', currentUser);
    
    if (isDevelopment) {
        console.log('🚀 Development mode: Always authenticated');
        console.log('🔐 ===== AUTHENTICATION CHECK COMPLETE (DEV) =====');
        return true; // Always authenticated in development
    }
    
    const authenticated = currentUser !== null;
    console.log('🔐 Authentication check result:', authenticated ? 'Yes' : 'No');
    console.log('🔐 User details:', currentUser);
    console.log('🔐 ===== AUTHENTICATION CHECK COMPLETE =====');
    return authenticated;
}

// Add auth state listener
export function onAuthStateChange(callback) {
    authStateListeners.push(callback);
    // Call immediately with current state
    if (currentUser !== undefined) {
        callback(currentUser);
    }
}

// Notify all auth state listeners
function notifyAuthStateListeners(user) {
    authStateListeners.forEach(callback => {
        try {
            callback(user);
        } catch (error) {
            console.error('Auth state listener error:', error);
        }
    });
}

// Update UI based on authentication state
function updateUIForAuthState(user) {
    console.log('🎨 ===== UPDATE UI FOR AUTH STATE START =====');
    console.log('🎨 Updating UI for auth state:', user ? 'authenticated' : 'not authenticated');
    console.log('🎨 Current pathname:', window.location.pathname);
    console.log('🎨 User object:', user);
    
    // Show/hide protected content
    const protectedElements = document.querySelectorAll('.protected-content');
    console.log('🎨 Found protected elements:', protectedElements.length);
    
    if (protectedElements.length === 0) {
        console.warn('⚠️ No .protected-content elements found on this page');
        console.warn('⚠️ This means protected content will not be shown/hidden');
    } else {
        console.log('🎨 Protected elements found:', Array.from(protectedElements).map(el => ({
            tagName: el.tagName,
            className: el.className,
            id: el.id,
            currentDisplay: el.style.display
        })));
    }
    
    protectedElements.forEach((element, index) => {
        const beforeDisplay = element.style.display;
        if (user) {
            console.log(`🎨 [${index}] Showing protected content element:`, {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                beforeDisplay: beforeDisplay
            });
            element.style.display = 'block';
            console.log(`🎨 [${index}] Element display changed from "${beforeDisplay}" to "${element.style.display}"`);
        } else {
            console.log(`🎨 [${index}] Hiding protected content element:`, {
                tagName: element.tagName,
                className: element.className,
                id: element.id,
                beforeDisplay: beforeDisplay
            });
            element.style.display = 'none';
            console.log(`🎨 [${index}] Element display changed from "${beforeDisplay}" to "${element.style.display}"`);
        }
    });
    
    // Update auth elements if they exist
    const authElements = document.querySelectorAll('[data-auth]');
    console.log('🎨 Found auth elements:', authElements.length);
    
    if (authElements.length > 0) {
        console.log('🎨 Auth elements found:', Array.from(authElements).map(el => ({
            tagName: el.tagName,
            dataAuth: el.dataset.auth,
            className: el.className,
            id: el.id
        })));
        
        authElements.forEach((element, index) => {
            const authType = element.dataset.auth;
            console.log(`🎨 [${index}] Processing auth element:`, {
                authType: authType,
                tagName: element.tagName,
                className: element.className,
                id: element.id
            });
            
            if (authType === 'user-info' && user) {
                console.log(`🎨 [${index}] Showing user info element`);
                element.style.display = 'block';
                element.innerHTML = `
                    <div class="user-info" style="display: flex; align-items: center; gap: 8px;">
                        <img src="${user.photoURL || '/assets/default-avatar.png'}" 
                             alt="Profile" 
                             class="user-avatar" 
                             style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.3);">
                        <span class="user-name" style="color: white; font-size: 14px; font-weight: 500;">
                            ${user.displayName || user.email}
                            ${isDevelopment ? '<span style="color: #ffd700; margin-left: 4px;">(DEV)</span>' : ''}
                        </span>
                    </div>
                `;
            } else if (authType === 'user-info' && !user) {
                console.log(`🎨 [${index}] Hiding user info element`);
                element.style.display = 'none';
            } else if (authType === 'sign-out' && user) {
                console.log(`🎨 [${index}] Showing sign out element`);
                element.style.display = 'block';
            } else if (authType === 'sign-out' && !user) {
                console.log(`🎨 [${index}] Hiding sign out element`);
                element.style.display = 'none';
            }
        });
    } else {
        console.log('🎨 No auth elements found on this page');
    }
    
    // Log final state
    console.log('🎨 Final UI state:', {
        protectedElementsCount: protectedElements.length,
        authElementsCount: authElements.length,
        userAuthenticated: !!user,
        pagePath: window.location.pathname
    });
    
    console.log('🎨 ===== UPDATE UI FOR AUTH STATE COMPLETE =====');
}

// Protect content - redirect to login if not authenticated
export function requireAuth() {
    if (isDevelopment) {
        console.log('🚀 Development mode: Authentication bypassed');
        return true; // Always allow access in development
    }
    
    if (!isAuthenticated()) {
        console.log('🚫 Authentication required but user not authenticated');
        // Don't redirect here - let the auth state change handler do it
        return false;
    }
    console.log('✅ Authentication check passed');
    return true;
}

// Show domain error message
function showDomainError() {
    console.log('🚫 Showing domain error message');
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.id = 'domain-error';
    errorDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #dc3545;
        color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        z-index: 10000;
        text-align: center;
        max-width: 400px;
        font-family: Arial, sans-serif;
    `;
    
    errorDiv.innerHTML = `
        <h3 style="margin: 0 0 15px 0; color: white;">🚫 Access Denied</h3>
        <p style="margin: 0 0 15px 0; line-height: 1.4;">
            Access to this application has been denied by your organization. 
            Your email domain is not authorized for this resource.
        </p>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">
            Please contact your administrator if you believe this is an error.
        </p>
    `;
    
    // Add to page
    document.body.appendChild(errorDiv);
    
    // Remove after 10 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 10000);
}

// Initialize auth when module loads
document.addEventListener('DOMContentLoaded', initAuth);
