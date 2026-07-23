import os
import pypdf
import docx
from io import BytesIO
from typing import Union

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text content from uploaded file bytes based on filename extension."""
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    
    try:
        if ext in ['.txt', '.md', '.markdown', '.json']:
            text = file_content.decode('utf-8', errors='ignore')
        elif ext == '.csv':
            import pandas as pd
            df = pd.read_csv(BytesIO(file_content))
            text = df.to_csv(index=False)
        elif ext in ['.xlsx', '.xls']:
            import pandas as pd
            df = pd.read_excel(BytesIO(file_content))
            text = df.to_csv(index=False)
        elif ext == '.pdf':
            pdf_file = BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif ext in ['.docx', '.doc']:
            docx_file = BytesIO(file_content)
            doc = docx.Document(docx_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            text = file_content.decode('utf-8', errors='ignore')
    except Exception as e:
        text = f"Error extracting text from {filename}: {str(e)}"
        
    return text.strip()
