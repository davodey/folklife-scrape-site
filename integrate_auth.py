#!/usr/bin/env python3
"""
Integrate Authentication into Static Site Generator
This script modifies your existing generator to add authentication
"""

import re
from pathlib import Path

def add_auth_to_html_template(html_content):
    """Add authentication elements to HTML template"""
    
    # Add authentication styles
    auth_styles = """
        /* Authentication Styles */
        .auth-loading-overlay {
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
        }
        
        .protected-content {
            display: none;
        }
        
        .auth-section {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-left: auto;
        }
        
        .user-info {
            display: none;
            align-items: center;
            gap: 0.5rem;
            color: white;
            font-size: 0.9rem;
        }
        
        .user-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .user-name {
            font-weight: 500;
        }
        
        .sign-out-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        
        .sign-out-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.5);
        }
    """
    
    # Add styles before closing </style> tag
    if '</style>' in html_content:
        html_content = html_content.replace('</style>', f'{auth_styles}\n    </style>')
    
    # Add protected-content class to container
    if 'class="container"' in html_content:
        html_content = html_content.replace('class="container"', 'class="container protected-content"')
    
    # Add authentication notice to header
    auth_notice = """
        <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
            🔐 <strong>Protected Content:</strong> You are authenticated and can view all layouts.
        </p>
    """
    
    # Find header and add notice
    header_pattern = r'(<div class="header">.*?<p>.*?</p>)'
    if re.search(header_pattern, html_content, re.DOTALL):
        html_content = re.sub(
            header_pattern, 
            r'\1' + auth_notice, 
            html_content, 
            flags=re.DOTALL
        )
    
    # Add authentication script before </body>
    auth_script = """
    <!-- Authentication Scripts -->
    <script type="module" src="./auth_middleware.js"></script>
    """
    
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', f'{auth_script}\n</body>')
    
    return html_content

def modify_generator_file():
    """Modify the generator file to add authentication"""
    
    generator_file = "generate_static_site_multi.py"
    
    if not Path(generator_file).exists():
        print(f"❌ {generator_file} not found!")
        return False
    
    print(f"📝 Modifying {generator_file}...")
    
    try:
        with open(generator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the generate_main_page function and modify it
        if 'def generate_main_page(' in content:
            # Add authentication to the HTML template
            content = add_auth_to_html_template(content)
            
            # Write back to file
            with open(generator_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Successfully modified generator file")
            return True
        else:
            print("❌ Could not find generate_main_page function")
            return False
            
    except Exception as e:
        print(f"❌ Error modifying file: {e}")
        return False

def copy_auth_files_to_docs():
    """Copy authentication files to docs directory"""
    
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    auth_files = ['auth.js', 'auth_middleware.js', 'login.html', 'test_auth.html']
    
    for auth_file in auth_files:
        source_path = Path(auth_file)
        dest_path = docs_dir / auth_file
        
        if source_path.exists():
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Copied {auth_file} to docs directory")
        else:
            print(f"⚠️  Source file {auth_file} not found")

def main():
    """Main integration function"""
    print("🔐 Integrating Authentication into Festival Crawler")
    print("=" * 60)
    
    # Step 1: Modify the generator file
    print("\n1. Modifying static site generator...")
    if not modify_generator_file():
        print("❌ Failed to modify generator file")
        return
    
    # Step 2: Copy authentication files
    print("\n2. Copying authentication files...")
    copy_auth_files_to_docs()
    
    print("\n" + "=" * 60)
    print("✅ Authentication integration complete!")
    print("\n📋 Next steps:")
    print("1. Run your generator: python generate_static_site_multi.py")
    print("2. Test authentication: open docs/test_auth.html")
    print("3. Verify pages require login")
    print("\n🔧 To test:")
    print("   cd docs && python -m http.server 8000")
    print("   Visit: http://localhost:8000/test_auth.html")

if __name__ == "__main__":
    main()
