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
    console.log('🔐 Initializing authentication...');
    console.log('🌐 Current domain:', window.location.hostname);
    console.log('🔗 Current URL:', window.location.href);
    
    if (isDevelopment) {
        console.log('🚀 Development mode: Authentication bypassed');
        // In development, simulate authenticated user
        currentUser = {
            uid: 'dev-user',
            email: 'developer@localhost',
            displayName: 'Local Developer',
            photoURL: null
        };
        updateUIForAuthState(currentUser);
        notifyAuthStateListeners(currentUser);
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
    
    onAuthStateChanged(auth, (user) => {
        console.log('🔄 Auth state changed:', user ? `User: ${user.email}` : 'No user');
        currentUser = user;
        updateUIForAuthState(user);
        notifyAuthStateListeners(user);
        
        if (user) {
            console.log('✅ User signed in:', user.email, window.location.pathname);
            console.log('📍 Current pathname:', window.location.pathname);
            // Redirect to main content if on login page
            if (window.location.pathname.includes('login.html') || window.location.pathname === '/') {
                // For GitHub Pages, use the correct base path
                const basePath = '/folklife-scrape-site';
                const redirectPath = basePath + '/index.html';
                console.log('🔄 Redirecting authenticated user to:', redirectPath);
                
                // Use a small delay to ensure the auth state is fully processed
                setTimeout(() => {
                    console.log('🚀 Executing redirect to:', redirectPath);
                    window.location.href = redirectPath;
                }, 100);
            } else {
                console.log('📍 User is authenticated but not on login page, no redirect needed');
            }
        } else {
            console.log('❌ User signed out');
            console.log('📍 Current pathname:', window.location.pathname);
            // Redirect to login if not authenticated
            if (!window.location.pathname.includes('login.html')) {
                const basePath = '/folklife-scrape-site';
                const loginPath = basePath + '/login.html';
                console.log('🔄 Redirecting unauthenticated user to:', loginPath);
                window.location.href = loginPath;
            } else {
                console.log('📍 User is not authenticated but already on login page, no redirect needed');
            }
        }
    });
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

// Sign out
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
    if (isDevelopment) {
        return true; // Always authenticated in development
    }
    return currentUser !== null;
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
    const authElements = document.querySelectorAll('[data-auth]');
    
    authElements.forEach(element => {
        const authType = element.dataset.auth;
        
        if (authType === 'user-info' && user) {
            element.style.display = 'block';
            element.innerHTML = `
                <div class="user-info">
                    <img src="${user.photoURL || '/assets/default-avatar.png'}" alt="Profile" class="user-avatar">
                    <span class="user-name">${user.displayName || user.email}</span>
                    ${isDevelopment ? '<span style="color: #ffd700;">(DEV)</span>' : ''}
                </div>
            `;
        } else if (authType === 'user-info' && !user) {
            element.style.display = 'none';
        } else if (authType === 'sign-out' && user) {
            element.style.display = 'block';
        } else if (authType === 'sign-out' && !user) {
            element.style.display = 'none';
        }
    });
}

// Protect content - redirect to login if not authenticated
export function requireAuth() {
    if (isDevelopment) {
        console.log('🚀 Development mode: Authentication bypassed');
        return true; // Always allow access in development
    }
    
    if (!isAuthenticated()) {
        const basePath = '/folklife-scrape-site';
        const loginPath = basePath + '/login.html';
        console.log('RequireAuth: Redirecting to:', loginPath);
        window.location.href = loginPath;
        return false;
    }
    return true;
}

// Initialize auth when module loads
document.addEventListener('DOMContentLoaded', initAuth);
