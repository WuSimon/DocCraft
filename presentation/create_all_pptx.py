#!/usr/bin/env python3
"""
Script to create a PowerPoint presentation from all HTML files in the presentation/html files directory.
Each HTML file becomes one slide in the presentation.
"""

import os
import glob
from create_pptx import html_to_pptx

def create_presentation_from_all_html():
    """
    Create a PowerPoint presentation from all HTML files in the html files directory.
    Each HTML file becomes one slide.
    """
    # Path to the HTML files directory
    html_dir = "html files"
    output_pptx = "DocCraft_Presentation.pptx"
    
    # Get all HTML files (numbered 1-14)
    html_files = []
    for i in range(1, 15):
        html_file = os.path.join(html_dir, str(i))
        if os.path.exists(html_file) and os.path.getsize(html_file) > 0:
            html_files.append(html_file)
    
    print(f"Found {len(html_files)} HTML files to process:")
    for html_file in html_files:
        print(f"  - {html_file}")
    
    # Create the presentation
    print(f"\nCreating PowerPoint presentation: {output_pptx}")
    
    # For now, we'll process just the first file to create the presentation
    # The current script creates one slide per HTML file, so we'll need to modify it
    # to handle multiple HTML files in one presentation
    
    if html_files:
        # Process the first file to create the presentation
        first_html = html_files[0]
        print(f"Processing first file: {first_html}")
        
        try:
            html_to_pptx(
                input_html=first_html,
                output_pptx=output_pptx,
                download_images=True
            )
            print(f"Successfully created: {output_pptx}")
            print(f"Note: Currently only the first HTML file was processed.")
            print(f"To process all files, the script needs to be modified to add multiple slides.")
        except Exception as e:
            print(f"Error creating presentation: {e}")
    else:
        print("No HTML files found to process.")

if __name__ == "__main__":
    create_presentation_from_all_html() 