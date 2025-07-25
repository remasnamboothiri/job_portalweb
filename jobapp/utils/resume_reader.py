import os
import fitz  # PyMuPDF
import docx

def extract_resume_text(resume_file):
    ext = os.path.splitext(resume_file.name)[1].lower()

    if ext == '.txt':
        return resume_file.read().decode('utf-8', errors='ignore')

    elif ext == '.docx':
        doc = docx.Document(resume_file)
        return '\n'.join([para.text for para in doc.paragraphs])

    elif ext == '.pdf':
        text = ''
        with fitz.open(stream=resume_file.read(), filetype="pdf") as pdf:
            for page in pdf:
                text += page.get_text()
        return text

    else:
        return "Unsupported file format."
