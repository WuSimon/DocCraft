from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_title_slide(prs):
    """Create the title slide."""
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "DocCraft"
    subtitle.text = "Intelligent Document Processing & Benchmarking\nSimon"
    
    # Style the title
    title.text_frame.paragraphs[0].font.size = Pt(44)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

def create_overview_slide(prs):
    """Create the overview slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    content = slide.placeholders[1]
    
    title.text = "What is DocCraft?"
    content.text = "• An intelligent Python package for document processing\n" \
                  "• Combines OCR, PDF extraction, and AI capabilities\n" \
                  "• Features comprehensive benchmarking tools\n" \
                  "• Designed for developers and researchers"

def create_features_slide(prs):
    """Create the features slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    content = slide.placeholders[1]
    
    title.text = "Key Features"
    content.text = "• Unified API for multiple OCR engines\n" \
                  "• Advanced preprocessing (deskew, binarization)\n" \
                  "• AI model integration (LayoutLM, Donut)\n" \
                  "• Comprehensive benchmarking tools\n" \
                  "• Standardized output formats (JSON/CSV)"

def create_use_case_slide(prs):
    """Create the use case slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    content = slide.placeholders[1]
    
    title.text = "Use Cases"
    content.text = "• Document digitization with performance tracking\n" \
                  "• Automated data extraction with benchmarking\n" \
                  "• Research data processing with metrics\n" \
                  "• Business document automation with optimization"

def create_roadmap_slide(prs):
    """Create the roadmap slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    content = slide.placeholders[1]
    
    title.text = "Development Roadmap"
    content.text = "Phase 1: Core Setup & Basic Parsers (1-2 weeks)\n" \
                  "Phase 2: Advanced Parsers & Preprocessing (2-3 weeks)\n" \
                  "Phase 3: Usability & Deployment (1 week)\n" \
                  "Future: Cloud API integration, CLI, Docker support"

def create_contact_slide(prs):
    """Create the contact slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Thank You!"
    
    # Add contact information
    left = Inches(2)
    top = Inches(2)
    width = Inches(6)
    height = Inches(2)
    
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.text = "Questions?"
    p = tf.add_paragraph()
    p.text = "GitHub: github.com/yourusername/DocCraft"
    p = tf.add_paragraph()
    p.text = "Email: your.email@example.com"

def create_presentation():
    """Create the complete presentation."""
    prs = Presentation()
    
    # Set slide dimensions to 16:9
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)
    
    # Create slides
    create_title_slide(prs)
    create_overview_slide(prs)
    create_features_slide(prs)
    create_use_case_slide(prs)
    create_roadmap_slide(prs)
    create_contact_slide(prs)
    
    # Save the presentation
    prs.save('DocCraft_Presentation.pptx')

if __name__ == "__main__":
    create_presentation() 