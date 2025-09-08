#!/usr/bin/env python3
"""
Create a valid PDF placeholder for candidate resume
"""

import os
from pathlib import Path

def create_minimal_pdf():
    """Create a minimal valid PDF file"""
    
    # Minimal PDF content that browsers can open
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Resume Placeholder) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
0000000348 00000 n 
0000000441 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
540
%%EOF"""
    
    return pdf_content

def main():
    """Create valid PDF placeholder"""
    
    # Ensure directory exists
    resume_dir = Path("media/candidate_resumes")
    resume_dir.mkdir(parents=True, exist_ok=True)
    
    # Create valid PDF
    pdf_path = resume_dir / "RAMA_S_NAMPOOTHIRY_CV.pdf"
    
    try:
        with open(pdf_path, 'wb') as f:
            f.write(create_minimal_pdf())
        
        print(f"Created valid PDF: {pdf_path}")
        print(f"File size: {pdf_path.stat().st_size} bytes")
        
        # Verify it's a valid PDF by checking header
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if header.startswith(b'%PDF-'):
                print("✅ Valid PDF header confirmed")
            else:
                print("❌ Invalid PDF header")
                
    except Exception as e:
        print(f"Error creating PDF: {e}")

if __name__ == "__main__":
    main()