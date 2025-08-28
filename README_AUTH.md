# Festival Crawler Authentication System

This project now includes a secure authentication system using Firebase Authentication with Google and Microsoft SSO support. All content is protected and requires user authentication to access.

## Features

- 🔐 **Secure Authentication**: Firebase-powered authentication system
- 🌐 **SSO Support**: Google and Microsoft account integration
- 🛡️ **Content Protection**: All pages require authentication
- 🎨 **Beautiful UI**: Modern, responsive login interface
- 📱 **Mobile Friendly**: Works seamlessly on all devices
- ⚡ **Fast Performance**: Optimized authentication flow

## Files Overview

- `auth.js` - Core Firebase authentication module
- `auth_middleware.js` - Authentication middleware for protected pages
- `login.html` - Beautiful login page with SSO options
- `index_protected.html` - Example protected content page
- `README_AUTH.md` - This setup guide

## Setup Instructions

### 1. Firebase Project Configuration

Your Firebase project is already configured with the following settings:
- **Project ID**: `folklife-e6f03`
- **API Key**: `AIzaSyCdOH2K3N79pb76zg6MTUK293Z3Rg-0tjQ`
- **Auth Domain**: `folklife-e6f03.firebaseapp.com`

### 2. Enable Authentication Providers

In your Firebase Console:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (`folklife-e6f03`)
3. Navigate to **Authentication** → **Sign-in method**
4. Enable the following providers:

#### Google Authentication
- Click on **Google**
- Enable it
- Add your authorized domain (e.g., `localhost` for development)
- Save

#### Microsoft Authentication
- Click on **Microsoft**
- Enable it
- Add your authorized domain
- Save

### 3. Authorized Domains

Add these domains to your Firebase project:
1. Go to **Authentication** → **Settings** → **Authorized domains**
2. Add your domains:
   - `localhost` (for development)
   - Your production domain (e.g., `yourdomain.com`)

### 4. Deploy Files

1. Upload all authentication files to your web server
2. Ensure the files are accessible via HTTPS (required for Firebase Auth)
3. Update any existing pages to include authentication

## Usage

### For Users

1. **Access the Site**: Navigate to any protected page
2. **Automatic Redirect**: Unauthenticated users are redirected to `/login.html`
3. **Choose SSO Provider**: Click either Google or Microsoft button
4. **Authenticate**: Complete the authentication flow
5. **Access Content**: Once authenticated, access all protected content
6. **Sign Out**: Use the sign-out button in the top toolbar

### For Developers

#### Protecting New Pages

To protect a new page, add this script tag:

```html
<script type="module" src="./auth_middleware.js"></script>
```

#### Adding Authentication UI

The middleware automatically adds:
- User profile information
- Sign-out button
- Loading states
- Authentication checks

#### Custom Authentication Logic

Use the exported functions from `auth.js`:

```javascript
import { 
    signInWithGoogle, 
    signInWithMicrosoft, 
    signOutUser, 
    getCurrentUser, 
    isAuthenticated 
} from './auth.js';

// Check if user is authenticated
if (isAuthenticated()) {
    // Show protected content
}

// Get current user info
const user = getCurrentUser();
console.log('User email:', user.email);
```

## Security Features

- **HTTPS Required**: Firebase Authentication requires HTTPS
- **Token Validation**: Automatic token validation and refresh
- **Session Management**: Secure session handling
- **CSRF Protection**: Built-in CSRF protection
- **Domain Restrictions**: Authorized domains only

## Troubleshooting

### Common Issues

1. **"Unauthorized Domain" Error**
   - Add your domain to Firebase authorized domains
   - Ensure you're using HTTPS

2. **"Popup Blocked" Error**
   - Allow pop-ups for your domain
   - Check browser pop-up blocker settings

3. **Authentication Not Working**
   - Verify Firebase configuration in `auth.js`
   - Check browser console for errors
   - Ensure authentication providers are enabled

4. **Redirect Loop**
   - Check file paths in authentication logic
   - Verify login.html is accessible

### Development vs Production

- **Development**: Use `localhost` in authorized domains
- **Production**: Add your production domain
- **Testing**: Test with both HTTP and HTTPS

## Customization

### Styling

- Modify CSS in `login.html` for login page styling
- Update styles in `auth_middleware.js` for toolbar elements
- Customize colors, fonts, and layouts as needed

### Authentication Flow

- Modify `auth.js` to add custom authentication logic
- Add additional providers (GitHub, Twitter, etc.)
- Implement custom user management

### Content Protection

- Use `requireAuth()` function to protect specific sections
- Add role-based access control
- Implement user permissions

## Performance Considerations

- **Lazy Loading**: Authentication modules are loaded on demand
- **Caching**: Firebase handles token caching automatically
- **Minimal Bundle**: Only essential authentication code is loaded
- **CDN**: Firebase SDKs are loaded from Google CDN

## Browser Support

- **Modern Browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **Mobile**: iOS Safari, Chrome Mobile, Samsung Internet
- **Legacy**: Internet Explorer 11+ (with polyfills)

## Support

For issues or questions:
1. Check the browser console for error messages
2. Verify Firebase project configuration
3. Test with different browsers and devices
4. Review Firebase documentation for authentication

## License

This authentication system is built on Firebase and follows their terms of service. Ensure compliance with Firebase usage policies and your application's privacy requirements.
