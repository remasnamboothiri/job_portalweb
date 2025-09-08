#!/usr/bin/env python3
"""
Fix static file paths in templates
"""

import os
import re
from pathlib import Path

def fix_template_static_paths():
    """Fix static file paths in all templates"""
    
    templates_dir = Path("templates")
    
    # Patterns to fix
    patterns_to_fix = [
        # Fix hero_1.jpg without static tag
        (r"url\('images/hero_1\.jpg'\)", "url('{% static 'images/hero_1.jpg' %}')"),
        (r'url\("images/hero_1\.jpg"\)', 'url("{% static \'images/hero_1.jpg\' %}")'),
        
        # Fix font paths without static tag
        (r'href="fonts/icomoon/style\.css"', 'href="{% static \'fonts/icomoon/style.css\' %}"'),
        (r'href="fonts/line-icons/style\.css"', 'href="{% static \'fonts/line-icons/style.css\' %}"'),
    ]
    
    fixed_files = []
    
    # Process all HTML files in templates directory
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all fixes
            for pattern, replacement in patterns_to_fix:
                content = re.sub(pattern, replacement, content)
            
            # Only write if content changed
            if content != original_content:
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_files.append(str(template_file))
                print(f"Fixed: {template_file}")
        
        except Exception as e:
            print(f"Error processing {template_file}: {e}")
    
    return fixed_files

def ensure_static_load_tags():
    """Ensure all templates have {% load static %} at the top"""
    
    templates_dir = Path("templates")
    
    for template_file in templates_dir.rglob("*.html"):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if template uses static files but doesn't load static
            if "{% static" in content and "{% load static %}" not in content:
                # Add {% load static %} at the top after any extends
                lines = content.split('\n')
                insert_index = 0
                
                # Find where to insert (after extends if present)
                for i, line in enumerate(lines):
                    if line.strip().startswith('{% extends'):
                        insert_index = i + 1
                        break
                
                lines.insert(insert_index, '{% load static %}')
                new_content = '\n'.join(lines)
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Added {{% load static %}} to: {template_file}")
        
        except Exception as e:
            print(f"Error processing {template_file}: {e}")

def main():
    """Main function"""
    print("Fixing template static file paths...")
    
    # Change to the correct directory
    os.chdir(Path(__file__).parent)
    
    # Fix static paths
    fixed_files = fix_template_static_paths()
    print(f"\nFixed {len(fixed_files)} template files")
    
    # Ensure static load tags
    print("\nEnsuring {% load static %} tags...")
    ensure_static_load_tags()
    
    print("\nTemplate fixes completed!")
    print("\nNext steps:")
    print("1. Test the application locally")
    print("2. Deploy to production")
    print("3. Check for any remaining 404 errors")

if __name__ == "__main__":
    main()