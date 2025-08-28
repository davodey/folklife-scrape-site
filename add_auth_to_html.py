#!/usr/bin/env python3
"""
Add Authentication to Existing HTML Files
This script adds Firebase authentication to your existing static HTML files
"""

import os
import re
from pathlib import Path

def add_auth_to_html(html_content, site_name):
    """Add authentication to HTML content"""
    
    # Check if authentication is already present
    if 'auth_middleware.js' in html_content:
        print(f"⚠️  Authentication already present, skipping...")
        return html_content
    
    # Add authentication styles to head
    auth_styles = """
        /* Authentication Styles */
        .protected-content { display: none; }
        .auth-loading { display: flex; align-items: center; justify-content: center; padding: 2rem; }
        .auth-loading::after { content: "🔐 Verifying authentication..."; font-size: 1.1rem; color: #666; }
        
        /* Site toolbar styles */
        .site-toolbar { 
            background: #34495e; 
            padding: 1rem 2rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .site-toggle { display: flex; gap: 0.5rem; }
        .site-btn { 
            padding: 0.75rem 1.5rem; 
            border: 2px solid white; 
            border-radius: 6px; 
            cursor: pointer; 
            font-weight: 500; 
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
            background: transparent;
            color: white;
        }
        .site-btn.active { 
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            border-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .site-btn:not(.active) { 
            background: transparent; 
            color: white; 
            border-color: rgba(255, 255, 255, 0.7);
        }
        .site-btn:hover:not(.active) { 
            background: rgba(255, 255, 255, 0.1); 
            border-color: white;
            transform: translateY(-1px);
        }
        .site-info { color: white; font-size: 0.9rem; opacity: 0.8; }
        
        /* Auth UI styles */
        .auth-section { display: flex; align-items: center; gap: 1rem; margin-left: auto; }
        .user-info { display: none; align-items: center; gap: 0.5rem; color: white; font-size: 0.9rem; }
        .user-avatar { width: 32px; height: 32px; border-radius: 50%; border: 2px solid rgba(255, 255, 255, 0.3); }
        .sign-out-btn { 
            background: rgba(255, 255, 255, 0.1); 
            color: white; 
            border: 1px solid rgba(255, 255, 255, 0.3); 
            padding: 0.5rem 1rem; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .sign-out-btn:hover { background: rgba(255, 255, 255, 0.2); }
    """
    
    # Add styles to head if not already present
    if '</style>' in html_content:
        html_content = html_content.replace('</style>', f'{auth_styles}\n    </style>')
    
    # Add protected-content class to main container if not already present
    if 'class="container"' in html_content and 'protected-content' not in html_content:
        html_content = html_content.replace('class="container"', 'class="container protected-content"')
    
    # Add authentication script before closing body tag (only if not already present)
    auth_script = """
    <!-- Authentication Scripts -->
    <script type="module" src="./auth_middleware.js"></script>
    """
    
    if '</body>' in html_content and 'auth_middleware.js' not in html_content:
        html_content = html_content.replace('</body>', f'{auth_script}\n</body>')
    
    # Add authentication notice to header (only if not already present)
    if '🔐 <strong>Protected Content:' not in html_content:
        auth_notice = f"""
        <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 0.5rem;">
            🔐 <strong>Protected Content:</strong> You are authenticated and can view all layouts.
        </p>
    """
        
        # Find the header section and add the notice
        header_pattern = r'(<div class="header">.*?<p>.*?</p>)'
        if re.search(header_pattern, html_content, re.DOTALL):
            html_content = re.sub(
                header_pattern, 
                r'\1' + auth_notice, 
                html_content, 
                flags=re.DOTALL
            )
    
    return html_content

def process_html_files(docs_dir):
    """Process all HTML files in the docs directory"""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"❌ Directory {docs_dir} not found!")
        return
    
    html_files = list(docs_path.glob('*.html'))
    print(f"Found {len(html_files)} HTML files to process")
    
    for html_file in html_files:
        print(f"Processing: {html_file.name}")
        
        try:
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine site name from filename
            site_name = 'festival'  # default
            if 'folklife' in html_file.name:
                site_name = 'folklife'
            
            # Add authentication
            modified_content = add_auth_to_html(content, site_name)
            
            # Write back to file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"✅ Added authentication to {html_file.name}")
            
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {e}")

def create_auth_files(docs_dir):
    """Create authentication files in the docs directory"""
    docs_path = Path(docs_dir)
    docs_path.mkdir(exist_ok=True)
    
    # Copy authentication files to docs directory
    auth_files = ['auth.js', 'auth_middleware.js', 'login.html']
    
    for auth_file in auth_files:
        source_path = Path(auth_file)
        dest_path = docs_path / auth_file
        
        if source_path.exists():
            # Copy the file
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Copied {auth_file} to docs directory")
        else:
            print(f"❌ Source file {auth_file} not found")

def main():
    """Main function"""
    print("🔐 Adding Authentication to Festival Crawler HTML Files")
    print("=" * 60)
    
    # Create authentication files in docs directory
    print("\n1. Creating authentication files...")
    create_auth_files('docs')
    
    # Process existing HTML files
    print("\n2. Adding authentication to HTML files...")
    process_html_files('docs')
    
    print("\n" + "=" * 60)
    print("✅ Authentication integration complete!")
    print("\n📋 Next steps:")
    print("1. Run your static site generator: python generate_static_site_multi.py")
    print("2. Test authentication: open docs/test_auth.html in your browser")
    print("3. Verify protected pages require login")
    print("\n🔧 To test locally:")
    print("   cd docs && python -m http.server 8000")
    print("   Then visit: http://localhost:8000/test_auth.html")

if __name__ == "__main__":
    main()
