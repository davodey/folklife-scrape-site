# 🔐 Quick Start - Festival Crawler Authentication

## 🚀 One-Command Setup

The easiest way to integrate authentication is to run the deployment script:

```bash
python deploy_auth.py
```

This will:
1. ✅ Copy authentication files to your docs directory
2. ✅ Generate your protected static site
3. ✅ Add authentication to all HTML files
4. ✅ Create a login redirect page

## 📋 Manual Setup (Alternative)

If you prefer to do it step by step:

### Step 1: Setup Authentication Files
```bash
python setup_auth.py
```

### Step 2: Integrate with Generator
```bash
python integrate_auth.py
```

### Step 3: Generate Protected Site
```bash
python generate_static_site_multi.py
```

### Step 4: Add Auth to Generated Files
```bash
python add_auth_to_html.py
```

## 🧪 Testing

### Local Testing
```bash
cd docs
python -m http.server 8000
```

Then visit:
- **Test Page**: http://localhost:8000/test_auth.html
- **Login Page**: http://localhost:8000/login.html
- **Protected Content**: Any other HTML file

### What to Test
1. ✅ Unauthenticated users are redirected to login
2. ✅ Google/Microsoft SSO works
3. ✅ Authenticated users can access content
4. ✅ Sign out works correctly
5. ✅ User info displays in toolbar

## 🔧 Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: `folklife-e6f03`
3. Enable **Google** and **Microsoft** authentication
4. Add `localhost` to authorized domains (for development)
5. Add your production domain when ready

## 📁 File Structure

```
festival-crawler/
├── auth.js                    # Firebase authentication
├── auth_middleware.js         # Authentication middleware
├── login.html                 # Beautiful login page
├── test_auth.html            # Authentication test page
├── deploy_auth.py            # One-command deployment
├── setup_auth.py             # Setup script
├── integrate_auth.py         # Integration script
├── add_auth_to_html.py       # Add auth to HTML files
├── docs/                     # Generated protected site
│   ├── index.html            # Protected main page
│   ├── login.html            # Login page
│   ├── test_auth.html        # Test page
│   └── [other protected files]
└── README_AUTH.md            # Detailed documentation
```

## 🚨 Troubleshooting

### Common Issues

1. **"Unauthorized Domain" Error**
   - Add your domain to Firebase authorized domains
   - Ensure you're using HTTPS (required for production)

2. **Authentication Not Working**
   - Check browser console for errors
   - Verify Firebase providers are enabled
   - Ensure pop-ups are allowed

3. **Redirect Loop**
   - Check file paths in authentication logic
   - Verify login.html is accessible

### Debug Mode

Open browser console and look for:
- Firebase initialization messages
- Authentication state changes
- Error messages

## 📱 Mobile Support

The authentication system works on:
- ✅ iOS Safari
- ✅ Chrome Mobile
- ✅ Samsung Internet
- ✅ All modern mobile browsers

## 🔒 Security Features

- **HTTPS Required**: Firebase Authentication requires HTTPS
- **Token Validation**: Automatic token validation and refresh
- **Session Management**: Secure session handling
- **CSRF Protection**: Built-in CSRF protection
- **Domain Restrictions**: Authorized domains only

## 🎯 Next Steps

After successful setup:

1. **Customize**: Modify colors, branding, and styling
2. **Add Providers**: Add GitHub, Twitter, or custom authentication
3. **User Management**: Implement user roles and permissions
4. **Analytics**: Add user activity tracking
5. **Deploy**: Upload to your production server

## 📞 Support

If you encounter issues:

1. Check the browser console for error messages
2. Verify Firebase project configuration
3. Test with different browsers and devices
4. Review Firebase documentation
5. Check this README for troubleshooting steps

---

**🎉 You're all set!** Your festival crawler now has enterprise-grade authentication with Google and Microsoft SSO.
