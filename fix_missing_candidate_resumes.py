#!/usr/bin/env python3
"""
Find and create missing candidate resume files
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.conf import settings
from jobapp.models import Candidate

def create_minimal_pdf():
    """Create a minimal valid PDF file"""
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
    """Find missing candidate resumes and create placeholders"""
    
    print("Finding missing candidate resume files...")
    
    # Get all candidates with resume files
    candidates = Candidate.objects.exclude(resume='').exclude(resume__isnull=True)
    
    missing_files = []
    existing_files = []
    
    for candidate in candidates:
        if candidate.resume:
            resume_path = os.path.join(settings.MEDIA_ROOT, str(candidate.resume))
            
            if os.path.exists(resume_path):
                existing_files.append(str(candidate.resume))
                print(f"EXISTS: {candidate.name} - {candidate.resume}")
            else:
                missing_files.append({
                    'candidate': candidate,
                    'path': resume_path,
                    'relative_path': str(candidate.resume)
                })
                print(f"MISSING: {candidate.name} - {candidate.resume}")
    
    print(f"\nSummary:")
    print(f"- Existing files: {len(existing_files)}")
    print(f"- Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\nCreating {len(missing_files)} placeholder PDF files...")
        
        # Ensure directory exists
        resume_dir = os.path.join(settings.MEDIA_ROOT, 'candidate_resumes')
        os.makedirs(resume_dir, exist_ok=True)
        
        created_count = 0
        for item in missing_files:
            try:
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(item['path']), exist_ok=True)
                
                # Create the PDF file
                with open(item['path'], 'wb') as f:
                    f.write(create_minimal_pdf())
                
                print(f"CREATED: {item['relative_path']}")
                created_count += 1
                
            except Exception as e:
                print(f"ERROR creating {item['relative_path']}: {e}")
        
        print(f"\nSuccessfully created {created_count} placeholder PDF files!")
    else:
        print("\nNo missing files found!")
    
    return len(missing_files)

if __name__ == "__main__":
    missing_count = main()
    if missing_count > 0:
        print(f"\nNext steps:")
        print(f"1. Commit and push the new PDF files")
        print(f"2. Test the 'View Resume' buttons")
        print(f"3. Replace placeholders with actual resumes when available")