"""
PDF Text Extraction Module
Extracts all text from Information_About_Colleges.pdf
"""

import pdfplumber
from pathlib import Path


def get_pdf_path():
    """Get the path to the PDF file in the project root."""
    return Path(__file__).parent.parent / "Information_About_Colleges.pdf"


def get_output_path():
    """Get the path for the output text file in the project root."""
    return Path(__file__).parent.parent / "extracted_text.txt"


def extract_text_from_pdf():
    """
    Extract all text from the PDF file.
    Process each page, skip pages with errors, and save the extracted text.
    """
    pdf_path = get_pdf_path()
    output_path = get_output_path()
    
    # Check if PDF file exists
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return
    
    all_text = []
    
    try:
        # Open the PDF file using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            # Iterate through each page in the PDF
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    # Print processing status for current page
                    print(f"Processing page {page_num} of {total_pages}...")
                    
                    # Extract text from the current page
                    page_text = page.extract_text()
                    
                    # Add page number header and extracted text to collection
                    all_text.append(f"\n--- Page {page_num} ---\n")
                    all_text.append(page_text)
                    
                except Exception as e:
                    # Skip pages with errors but continue processing remaining pages
                    print(f"Warning: Error processing page {page_num}: {str(e)}")
                    all_text.append(f"\n--- Page {page_num} (Error: {str(e)}) ---\n")
                    continue
        
        # Save all extracted text to output file in project root
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(all_text)
        
        # Print completion message
        print("Extraction Completed Successfully.")
        
    except Exception as e:
        print(f"Error opening PDF file: {str(e)}")


if __name__ == "__main__":
    extract_text_from_pdf()
