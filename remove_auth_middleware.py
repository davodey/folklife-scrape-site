#!/usr/bin/env python3
"""
Remove auth_middleware.js script from all HTML files to eliminate conflicts
"""

import os
from pathlib import Path

def remove_auth_middleware(html_content):
    """Remove auth_middleware.js script tag"""
    
    # Remove the auth_middleware.js script tag
    if 'auth_middleware.js' in html_content:
        # Remove the entire script tag
        html_content = html_content.replace('<script type="module" src="./auth_middleware.js"></script>', '')
        return html_content, True
    
    return html_content, False

def process_html_files():
    """Process all HTML files in the docs directory"""
    
    docs_dir = Path('docs')
    if not docs_dir.exists():
        print("❌ docs directory not found")
        return
    
    html_files = list(docs_dir.glob('*.html'))
    print(f"🔍 Found {len(html_files)} HTML files to process")
    
    modified_count = 0
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove auth_middleware.js
            new_content, was_modified = remove_auth_middleware(content)
            
            if was_modified:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modified_count += 1
                print(f"✅ Removed auth_middleware.js from {html_file.name}")
            
        except Exception as e:
            print(f"❌ Error processing {html_file.name}: {e}")
    
    print(f"\n🎉 Completed! Modified {modified_count} files")

if __name__ == "__main__":
    process_html_files()
