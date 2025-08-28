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
export const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1' || 
                     window.location.hostname.includes('localhost');

export const isProduction = !isDevelopment;

console.log(`🔍 Environment detected: ${isDevelopment ? 'Development' : 'Production'}`);

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
    onAuthStateChanged(auth, (user) => {
        currentUser = user;
        updateUIForAuthState(user);
        notifyAuthStateListeners(user);
        
        if (user) {
            console.log('User signed in:', user.email);
            // Redirect to main content if on login page
            if (window.location.pathname === '/login.html' || window.location.pathname === '/') {
                // Use absolute URL in production, relative in development
                const mainUrl = isProduction 
                    ? 'https://davodey.github.io/folklife-scrape-site/'
                    : '/index.html';
                window.location.href = mainUrl;
            }
        } else {
            console.log('User signed out');
            // Redirect to login if not authenticated
            if (!window.location.pathname.includes('login.html')) {
                // Use absolute URL in production, relative in development
                const loginUrl = isProduction 
                    ? 'https://davodey.github.io/folklife-scrape-site/login.html'
                    : '/login.html';
                window.location.href = loginUrl;
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
        const result = await signInWithPopup(auth, googleProvider);
        return result.user;
    } catch (error) {
        console.error('Google sign-in error:', error);
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
        const result = await signInWithPopup(auth, microsoftProvider);
        return result.user;
    } catch (error) {
        console.error('Microsoft sign-in error:', error);
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
        // Use absolute URL in production, relative in development
        const loginUrl = isProduction 
            ? 'https://davodey.github.io/folklife-scrape-site/login.html'
            : '/login.html';
        window.location.href = loginUrl;
    } catch (error) {
        console.error('Sign-out error:', error);
        throw error;
    }
}

// Get current user
export function getCurrentUser() {
    // Return local state if available, otherwise check Firebase
    return currentUser || auth.currentUser;
}

// Check if user is authenticated
export function isAuthenticated() {
    if (isDevelopment) {
        return true; // Always authenticated in development
    }
    // Check both local state and Firebase auth state
    return currentUser !== null || auth.currentUser !== null;
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
        // Use absolute URL in production, relative in development
        const loginUrl = isProduction 
            ? 'https://davodey.github.io/folklife-scrape-site/login.html'
            : '/login.html';
        window.location.href = loginUrl;
        return false;
    }
    return true;
}

// Initialize auth immediately and also when DOM is ready
initAuth();

// Also initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initAuth);

// Ensure auth state is checked on every page load
window.addEventListener('load', () => {
    // Check if user is already authenticated
    const user = auth.currentUser;
    if (user) {
        console.log('User already authenticated on page load:', user.email);
        currentUser = user;
        updateUIForAuthState(user);
        notifyAuthStateListeners(user);
    }
});
