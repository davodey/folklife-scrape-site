#!/usr/bin/env python3
"""
Fix Authentication Scripts in HTML Files

This script adds the missing auth.js script to all HTML files that have auth_middleware.js
but are missing the required auth.js dependency.
"""

import os
import re
from pathlib import Path

def fix_auth_scripts():
    """Fix authentication scripts in all HTML files."""
    
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ docs directory not found!")
        return
    
    # Find all HTML files
    html_files = list(docs_dir.glob("*.html"))
    print(f"🔍 Found {len(html_files)} HTML files")
    
    fixed_count = 0
    already_fixed_count = 0
    
    for html_file in html_files:
        print(f"\n📄 Processing: {html_file.name}")
        
        # Read the file content
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {html_file.name}: {e}")
            continue
        
        # Check if auth_middleware.js is present
        if './auth_middleware.js' not in content:
            print(f"⏭️  Skipping {html_file.name} - no auth_middleware.js found")
            continue
        
        # Check if auth.js is already present
        if './auth.js' in content:
            print(f"✅ {html_file.name} already has auth.js")
            already_fixed_count += 1
            continue
        
        # Find the line with auth_middleware.js and add auth.js before it
        pattern = r'(\s*<!-- Authentication Scripts -->\s*\n\s*<script type="module" src="\./auth_middleware\.js"></script>)'
        replacement = r'\1\n    <script type="module" src="./auth.js"></script>'
        
        # Try to replace
        new_content = re.sub(pattern, replacement, content)
        
        # If that didn't work, try a different approach
        if new_content == content:
            # Look for the auth_middleware.js script tag and add auth.js before it
            pattern = r'(<script type="module" src="\./auth_middleware\.js"></script>)'
            replacement = r'    <script type="module" src="./auth.js"></script>\n\1'
            new_content = re.sub(pattern, replacement, content)
        
        # If still no change, try to add it before the closing body tag
        if new_content == content:
            pattern = r'(</body>)'
            replacement = r'    <!-- Authentication Scripts -->\n    <script type="module" src="./auth.js"></script>\n    <script type="module" src="./auth_middleware.js"></script>\n\1'
            new_content = re.sub(pattern, replacement, content)
        
        # Check if we made a change
        if new_content != content:
            # Write the updated content back
            try:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Fixed {html_file.name} - added auth.js")
                fixed_count += 1
            except Exception as e:
                print(f"❌ Error writing {html_file.name}: {e}")
        else:
            print(f"⚠️  Could not fix {html_file.name} - no suitable location found")
    
    print(f"\n🎯 Summary:")
    print(f"✅ Fixed: {fixed_count} files")
    print(f"✅ Already correct: {already_fixed_count} files")
    print(f"📊 Total processed: {len(html_files)} files")

if __name__ == "__main__":
    fix_auth_scripts()
