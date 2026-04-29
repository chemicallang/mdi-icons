#!/usr/bin/env python
import os
import re
import zipfile
import urllib.request
import shutil

# Templarian/MaterialDesign repository
# We will use the zip of the repository and look for the 'svg' directory
ZIP_URL = "https://github.com/Templarian/MaterialDesign/archive/refs/heads/master.zip"
ZIP_FILE = "mdi_icons.zip"
EXTRACT_DIR = "mdi_icons_temp"
OUTPUT_DIR = "src"

def to_pascal_case(name):
    return ''.join(word.capitalize() for word in name.split('-'))

def generate_icons():
    # 1. Download
    if not os.path.exists(ZIP_FILE):
        print(f"Downloading {ZIP_URL}...")
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(ZIP_URL, ZIP_FILE)
    
    # 2. Extract
    if not os.path.exists(EXTRACT_DIR):
        print(f"Extracting {ZIP_FILE}...")
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

    # 3. Find svg directory
    # The new repo structure should be: MaterialDesign-master/svg/
    base_svg_dir = ""
    for root, dirs, files in os.walk(EXTRACT_DIR):
        if root.endswith("svg") and os.path.isdir(root):
            base_svg_dir = root
            break
            
    if not base_svg_dir:
        print("Error: Could not find svg directory")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    conflicting_names = { "Sleep" : True }

    print(f"Generating icon components from {base_svg_dir}...")
    
    count = 0
    for filename in os.listdir(base_svg_dir):
        if filename.endswith(".svg"):
            icon_name = filename[:-4]
            svg_path = os.path.join(base_svg_dir, filename)
            
            with open(svg_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract inner SVG content (paths, etc.)
            inner_match = re.search(r'<svg[^>]*>(.*)</svg>', content, re.DOTALL)
            if inner_match:
                inner_content = inner_match.group(1).strip()
                # Clean up: remove explicit fills
                inner_content = re.sub(r' fill="[^"]*"', '', inner_content)
                
                pascal_name = to_pascal_case(icon_name)

                # Handle names starting with numbers
                if pascal_name[0].isdigit():
                    pascal_name = "Icon" + pascal_name

                # Handle conflicting names
                component_name = pascal_name
                if component_name in conflicting_names:
                    component_name = component_name + "Icon"

                # Wrap in a new component
                component_code = f"""public #universal {component_name}(props) {{
    return <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" {{...props}}>
        {inner_content}
    </svg>
}}
"""
                output_file = os.path.join(OUTPUT_DIR, f"{pascal_name}.ch")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(component_code)
                count += 1
    
    print(f"Successfully generated {count} icons in {OUTPUT_DIR}/")

if __name__ == "__main__":
    generate_icons()
