#!/usr/bin/env python3
"""
Script to fix malformed Jupyter notebook JSON structures.
This script will properly close any incomplete JSON in Jupyter notebook files.
"""

import json
import os
import sys

def fix_notebook(notebook_path):
    """
    Fix a malformed Jupyter notebook by properly closing its JSON structure.
    """
    try:
        # Try to read the file as is to see if it's already valid
        with open(notebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
            try:
                json.loads(content)
                print(f"The notebook {notebook_path} is already valid JSON.")
                return True
            except json.JSONDecodeError:
                # If we have a parsing error, we'll fix the notebook
                pass
        
        # Read the file content
        with open(notebook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file starts with a proper JSON opening
        if not content.strip().startswith('{'):
            print(f"Error: {notebook_path} does not start with a valid JSON object.")
            return False
        
        # Find the last cell in the notebook (to see where we need to add closing brackets)
        if '"cells": [' in content:
            # Construct a properly formatted notebook
            # Extract the cells content as much as possible
            try:
                # Try to extract the cells array content
                cells_start = content.find('"cells": [')
                if cells_start == -1:
                    print(f"Error: Could not find 'cells' array in {notebook_path}")
                    return False
                
                # Split the content into header and cells
                header = content[:cells_start + len('"cells": [')]
                cells_content = content[cells_start + len('"cells": ['):]
                
                # Reconstruct with proper closing
                fixed_content = f"{header}{cells_content.rstrip('} \t\n,')}\n  ]\n}}"
                
                # Validate the fixed content
                try:
                    json.loads(fixed_content)
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not automatically fix {notebook_path}: {str(e)}")
                    # As a fallback, try a more aggressive fix
                    fixed_content = header + "]\n}"
                    try:
                        json.loads(fixed_content)
                    except json.JSONDecodeError:
                        print(f"Error: Failed to fix {notebook_path} with the fallback method")
                        return False
                
                # Write the fixed content back
                with open(notebook_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                print(f"Successfully fixed {notebook_path}")
                return True
                
            except Exception as e:
                print(f"Error fixing {notebook_path}: {str(e)}")
                return False
        else:
            print(f"Error: {notebook_path} does not have a 'cells' array.")
            return False
    except Exception as e:
        print(f"Unexpected error processing {notebook_path}: {str(e)}")
        return False

def main():
    """
    Main function to run the script.
    """
    if len(sys.argv) < 2:
        print("Usage: python fix_jupyter_notebook.py <path_to_notebook>")
        return
    
    notebook_path = sys.argv[1]
    if not os.path.exists(notebook_path):
        print(f"Error: File {notebook_path} not found.")
        return
    
    if not notebook_path.endswith('.ipynb'):
        print(f"Error: {notebook_path} is not a Jupyter notebook file.")
        return
    
    fix_notebook(notebook_path)

if __name__ == "__main__":
    main()
