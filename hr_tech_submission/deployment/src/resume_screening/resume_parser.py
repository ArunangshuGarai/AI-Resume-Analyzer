"""
Resume parsing and text extraction module
"""

import PyPDF2
import docx
from pathlib import Path
import re
from typing import Dict, List, Optional

class ResumeParser:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from resume file based on extension"""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return self.extract_text_from_docx(file_path)
        elif extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\;\:\(\)\-\+\@\#]', ' ', text)
        
        return text
    
    def extract_basic_info(self, text: str) -> Dict[str, any]:
        """Extract basic information from resume text"""
        info = {
            'email': None,
            'phone': None,
            'name': None
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            info['email'] = email_match.group()
        
        # Extract phone number
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\b\d{10}\b'
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                info['phone'] = phone_match.group()
                break
        
        # Extract name (assume first line or first few words after cleaning)
        lines = text.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if len(line) > 2 and len(line.split()) <= 4:  # Reasonable name length
                # Check if line contains mostly alphabetic characters
                if re.match(r'^[A-Za-z\s\.]+$', line):
                    info['name'] = line
                    break
        
        return info
    
    def parse_resume(self, file_path: str) -> Dict[str, any]:
        """Parse resume and extract all relevant information"""
        try:
            # Extract raw text
            raw_text = self.extract_text(file_path)
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            
            # Extract basic info
            basic_info = self.extract_basic_info(raw_text)
            
            return {
                'file_path': file_path,
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'basic_info': basic_info,
                'word_count': len(cleaned_text.split()),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'raw_text': None,
                'cleaned_text': None,
                'basic_info': None,
                'word_count': 0,
                'success': False,
                'error': str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with sample resume files
    sample_files = [
        "data/resumes/john_smith_resume.txt",
        "data/resumes/sarah_johnson_resume.txt"
    ]
    
    for file_path in sample_files:
        if Path(file_path).exists():
            print(f"\n📄 Parsing: {file_path}")
            result = parser.parse_resume(file_path)
            
            if result['success']:
                print(f"✅ Success - {result['word_count']} words")
                print(f"📧 Email: {result['basic_info']['email']}")
                print(f"👤 Name: {result['basic_info']['name']}")
                print(f"📱 Phone: {result['basic_info']['phone']}")
            else:
                print(f"❌ Error: {result['error']}")
        else:
            print(f"⚠️ File not found: {file_path}")