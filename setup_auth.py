#!/usr/bin/env python3
"""
Authentication System Setup Script
Helps set up and verify the Firebase authentication system
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def check_file_exists(filepath):
    """Check if a file exists and return status"""
    path = Path(filepath)
    if path.exists():
        return True, path.stat().st_size
    return False, 0

def verify_firebase_config():
    """Verify Firebase configuration in auth.js"""
    print_step("1", "Verifying Firebase Configuration")
    
    if not check_file_exists("auth.js")[0]:
        print("❌ auth.js not found!")
        return False
    
    try:
        with open("auth.js", "r") as f:
            content = f.read()
        
        # Check for required Firebase config
        required_keys = [
            "apiKey",
            "authDomain", 
            "projectId",
            "storageBucket",
            "messagingSenderId",
            "appId",
            "measurementId"
        ]
        
        config_found = True
        for key in required_keys:
            if key not in content:
                print(f"❌ Missing Firebase config key: {key}")
                config_found = False
        
        if config_found:
            print("✅ Firebase configuration found in auth.js")
            
            # Extract and display config
            start = content.find("const firebaseConfig = {")
            if start != -1:
                end = content.find("};", start) + 2
                config_section = content[start:end]
                print("\n📋 Firebase Configuration:")
                print(config_section)
            
            return True
        else:
            print("❌ Firebase configuration incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error reading auth.js: {e}")
        return False

def check_required_files():
    """Check if all required authentication files exist"""
    print_step("2", "Checking Required Files")
    
    required_files = [
        "auth.js",
        "auth_middleware.js", 
        "login.html",
        "index_protected.html",
        "test_auth.html"
    ]
    
    all_files_exist = True
    total_size = 0
    
    for file in required_files:
        exists, size = check_file_exists(file)
        if exists:
            print(f"✅ {file} ({size:,} bytes)")
            total_size += size
        else:
            print(f"❌ {file} - MISSING")
            all_files_exist = False
    
    if all_files_exist:
        print(f"\n✅ All required files present (Total: {total_size:,} bytes)")
        return True
    else:
        print("\n❌ Some required files are missing")
        return False

def check_firebase_dependencies():
    """Check if Firebase dependencies are properly configured"""
    print_step("3", "Checking Firebase Dependencies")
    
    try:
        with open("auth.js", "r") as f:
            content = f.read()
        
        # Check for Firebase SDK imports
        firebase_imports = [
            "firebase/app",
            "firebase/auth", 
            "firebase/analytics"
        ]
        
        all_imports_found = True
        for import_path in firebase_imports:
            if import_path in content:
                print(f"✅ Firebase import found: {import_path}")
            else:
                print(f"❌ Firebase import missing: {import_path}")
                all_imports_found = False
        
        # Check for auth providers
        providers = ["GoogleAuthProvider", "OAuthProvider"]
        for provider in providers:
            if provider in content:
                print(f"✅ Auth provider found: {provider}")
            else:
                print(f"❌ Auth provider missing: {provider}")
                all_imports_found = False
        
        return all_imports_found
        
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def generate_firebase_setup_guide():
    """Generate Firebase setup instructions"""
    print_step("4", "Firebase Setup Instructions")
    
    setup_guide = """
🔧 FIREBASE SETUP STEPS:

1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project: folklife-e6f03
3. Navigate to Authentication → Sign-in method
4. Enable Google Authentication:
   - Click "Google"
   - Enable it
   - Add authorized domain (localhost for development)
   - Save

5. Enable Microsoft Authentication:
   - Click "Microsoft" 
   - Enable it
   - Add authorized domain
   - Save

6. Add Authorized Domains:
   - Go to Authentication → Settings → Authorized domains
   - Add: localhost (for development)
   - Add your production domain when ready

7. Test Authentication:
   - Open test_auth.html in your browser
   - Try signing in with Google or Microsoft
   - Verify authentication works

⚠️  IMPORTANT NOTES:
- HTTPS is required for production
- Test with localhost first
- Check browser console for errors
- Ensure pop-ups are allowed
"""
    
    print(setup_guide)
    
    # Save setup guide to file
    with open("FIREBASE_SETUP_GUIDE.txt", "w") as f:
        f.write(setup_guide)
    
    print("📝 Setup guide saved to FIREBASE_SETUP_GUIDE.txt")

def test_local_server():
    """Test if files can be served locally"""
    print_step("5", "Testing Local Server Setup")
    
    print("To test the authentication system locally:")
    print("\n1. Start a local HTTP server:")
    print("   Python 3: python -m http.server 8000")
    print("   Python 2: python -m SimpleHTTPServer 8000")
    print("   Node.js: npx http-server")
    
    print("\n2. Open in browser:")
    print("   http://localhost:8000/test_auth.html")
    print("   http://localhost:8000/login.html")
    
    print("\n3. Test authentication flow:")
    print("   - Try accessing protected pages")
    print("   - Test Google/Microsoft sign-in")
    print("   - Verify redirects work correctly")

def main():
    """Main setup function"""
    print_header("Festival Crawler Authentication Setup")
    
    print("This script will help you set up and verify the Firebase authentication system.")
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"\n📁 Current directory: {current_dir}")
    
    # Verify Firebase configuration
    if not verify_firebase_config():
        print("\n❌ Firebase configuration issues found!")
        print("Please check your auth.js file.")
        return False
    
    # Check required files
    if not check_required_files():
        print("\n❌ Missing required files!")
        print("Please ensure all authentication files are present.")
        return False
    
    # Check dependencies
    if not check_firebase_dependencies():
        print("\n❌ Firebase dependencies issues found!")
        print("Please check your auth.js file.")
        return False
    
    # Generate setup guide
    generate_firebase_setup_guide()
    
    # Test local server
    test_local_server()
    
    print_header("Setup Complete!")
    print("✅ Authentication system is properly configured")
    print("📖 Review FIREBASE_SETUP_GUIDE.txt for next steps")
    print("🧪 Test with test_auth.html to verify everything works")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)
