#!/usr/bin/env python3
"""
Clean up duplicate authentication scripts from HTML files
"""

import re
from pathlib import Path

def clean_duplicate_auth(html_content):
    """Remove duplicate authentication scripts and keep only one set"""
    
    # Find all authentication script sections
    auth_pattern = r'<!-- Authentication Scripts -->\s*<script type="module" src="\./auth_middleware\.js"></script>\s*'
    
    # Count how many we have
    matches = re.findall(auth_pattern, html_content)
    
    if len(matches) > 1:
        print(f"Found {len(matches)} duplicate auth script sections, cleaning up...")
        
        # Keep only the first occurrence
        first_match = matches[0]
        html_content = re.sub(auth_pattern, '', html_content)
        
        # Add back just one set before </body>
        if '</body>' in html_content:
            clean_auth_script = f"""
    {first_match.strip()}
</body>"""
            html_content = html_content.replace('</body>', clean_auth_script)
    
    # Also clean up duplicate auth.js scripts
    auth_js_pattern = r'<script type="module" src="\./auth\.js"></script>\s*'
    auth_js_matches = re.findall(auth_js_pattern, html_content)
    
    if len(auth_js_matches) > 1:
        print(f"Found {len(auth_js_matches)} duplicate auth.js scripts, cleaning up...")
        
        # Remove all auth.js scripts
        html_content = re.sub(auth_js_pattern, '', html_content)
        
        # Add back just one before the auth middleware
        if 'auth_middleware.js' in html_content:
            # Find the auth middleware script and add auth.js before it
            middleware_pattern = r'(<!-- Authentication Scripts -->\s*<script type="module" src="\./auth_middleware\.js"></script>)'
            html_content = re.sub(middleware_pattern, r'<script type="module" src="./auth.js"></script>\n    \1', html_content)
    
    return html_content

def process_html_files(docs_dir):
    """Process all HTML files in the docs directory to remove duplicates"""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"❌ Directory {docs_dir} not found!")
        return
    
    html_files = list(docs_path.glob('*.html'))
    print(f"Found {len(html_files)} HTML files to clean up")
    
    cleaned_count = 0
    for html_file in html_files:
        print(f"Processing: {html_file.name}")
        
        try:
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if there are duplicates
            auth_pattern = r'<!-- Authentication Scripts -->\s*<script type="module" src="\./auth_middleware\.js"></script>\s*'
            matches = re.findall(auth_pattern, content)
            
            if len(matches) > 1:
                print(f"  🧹 Found {len(matches)} duplicate auth sections, cleaning...")
                cleaned_content = clean_duplicate_auth(content)
                
                # Write back to file
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                cleaned_count += 1
                print(f"  ✅ Cleaned {html_file.name}")
            else:
                print(f"  ✅ No duplicates found in {html_file.name}")
            
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {e}")
    
    print(f"\n🎉 Cleanup complete! Cleaned {cleaned_count} files with duplicates.")

def main():
    """Main function"""
    print("🧹 Cleaning up duplicate authentication scripts")
    print("=" * 50)
    
    process_html_files('docs')
    
    print("\n📋 Next steps:")
    print("1. Run add_auth_to_html.py again to ensure clean authentication")
    print("2. Test the authentication flow")
    print("3. Verify redirects are working correctly")

if __name__ == "__main__":
    main()
