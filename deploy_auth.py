#!/usr/bin/env python3
"""
Deploy Authentication System
Complete setup and deployment of the authentication system
"""

import os
import shutil
from pathlib import Path

def check_prerequisites():
    """Check if all required files exist"""
    print("🔍 Checking prerequisites...")
    
    required_files = [
        'auth.js',
        'auth_middleware.js', 
        'login.html',
        'test_auth.html',
        'generate_static_site_multi.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files found")
    return True

def setup_docs_directory():
    """Set up the docs directory with authentication files"""
    print("\n📁 Setting up docs directory...")
    
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Copy authentication files
    auth_files = ['auth.js', 'auth_middleware.js', 'login.html', 'test_auth.html']
    
    for auth_file in auth_files:
        source = Path(auth_file)
        dest = docs_dir / auth_file
        
        if source.exists():
            shutil.copy2(source, dest)
            print(f"✅ Copied {auth_file}")
        else:
            print(f"❌ Source file {auth_file} not found")
            return False
    
    return True

def generate_protected_site():
    """Generate the protected static site"""
    print("\n🚀 Generating protected static site...")
    
    try:
        # Run the static site generator
        import subprocess
        result = subprocess.run(['python', 'generate_static_site_multi.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Static site generated successfully")
            print(result.stdout)
        else:
            print("❌ Error generating static site:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running generator: {e}")
        return False
    
    return True

def add_auth_to_generated_files():
    """Add authentication to generated HTML files"""
    print("\n🔐 Adding authentication to generated files...")
    
    docs_dir = Path("docs")
    html_files = list(docs_dir.glob('*.html'))
    
    # Skip authentication files
    auth_files = {'login.html', 'test_auth.html'}
    html_files = [f for f in html_files if f.name not in auth_files]
    
    print(f"Found {len(html_files)} HTML files to protect")
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add protected-content class to container
            if 'class="container"' in content:
                content = content.replace('class="container"', 'class="container protected-content"')
            
            # Add authentication script
            auth_script = """
    <!-- Authentication Scripts -->
    <script type="module" src="./auth_middleware.js"></script>
    """
            
            if '</body>' in content:
                content = content.replace('</body>', f'{auth_script}\n</body>')
            
            # Write back
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Protected {html_file.name}")
            
        except Exception as e:
            print(f"❌ Error protecting {html_file.name}: {e}")
            return False
    
    return True

def create_index_redirect():
    """Create index.html that redirects to login"""
    print("\n🔄 Creating login redirect...")
    
    docs_dir = Path("docs")
    index_file = docs_dir / "index_redirect.html"
    
    redirect_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Redirecting to Login...</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            color: white;
            text-align: center;
        }
        .redirect-container {
            background: rgba(255, 255, 255, 0.1);
            padding: 2rem;
            border-radius: 16px;
            backdrop-filter: blur(20px);
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="redirect-container">
        <div class="spinner"></div>
        <h2>Redirecting to Login...</h2>
        <p>Please wait while we redirect you to the secure login page.</p>
        <p><a href="./login.html" style="color: white; text-decoration: underline;">Click here if not redirected automatically</a></p>
    </div>
    
    <script>
        // Redirect to login page
        setTimeout(() => {
            window.location.href = './login.html';
        }, 2000);
    </script>
</body>
</html>"""
    
    try:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(redirect_html)
        print("✅ Created login redirect page")
        return True
    except Exception as e:
        print(f"❌ Error creating redirect: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Deploying Festival Crawler Authentication System")
    print("=" * 60)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please ensure all files are present.")
        return
    
    # Step 2: Setup docs directory
    if not setup_docs_directory():
        print("\n❌ Failed to setup docs directory.")
        return
    
    # Step 3: Generate protected site
    if not generate_protected_site():
        print("\n❌ Failed to generate static site.")
        return
    
    # Step 4: Add authentication to generated files
    if not add_auth_to_generated_files():
        print("\n❌ Failed to add authentication to files.")
        return
    
    # Step 5: Create login redirect
    if not create_index_redirect():
        print("\n❌ Failed to create login redirect.")
        return
    
    print("\n" + "=" * 60)
    print("🎉 Authentication system deployed successfully!")
    print("\n📋 What was created:")
    print("✅ Authentication files in docs/ directory")
    print("✅ Protected HTML pages")
    print("✅ Login redirect page")
    print("✅ Test authentication page")
    
    print("\n🧪 To test the system:")
    print("1. Start local server: cd docs && python -m http.server 8000")
    print("2. Visit: http://localhost:8000/test_auth.html")
    print("3. Try accessing protected pages (they should redirect to login)")
    print("4. Sign in with Google or Microsoft")
    
    print("\n🔧 Production deployment:")
    print("1. Upload docs/ directory to your web server")
    print("2. Ensure HTTPS is enabled (required for Firebase)")
    print("3. Add your domain to Firebase authorized domains")
    print("4. Test authentication flow")
    
    print("\n📖 For more details, see README_AUTH.md")

if __name__ == "__main__":
    main()
