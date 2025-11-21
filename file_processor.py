import os
import PyPDF2
import docx

class FileProcessor:
    """
    Handles processing of various file formats for investment deal documents.
    Supports: .txt, .pdf, .doc, .docx, .md
    """
    
    def process_file(self, filepath):
        """
        Process a file and extract text content.
        
        Args:
            filepath: Path to the file to process
            
        Returns:
            Extracted text content as string
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        file_ext = os.path.splitext(filepath)[1].lower()
        
        if file_ext == '.txt' or file_ext == '.md':
            return self._process_text_file(filepath)
        elif file_ext == '.pdf':
            return self._process_pdf_file(filepath)
        elif file_ext == '.doc' or file_ext == '.docx':
            return self._process_docx_file(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _process_text_file(self, filepath):
        """Process plain text or markdown files"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _process_pdf_file(self, filepath):
        """Process PDF files"""
        try:
            text_content = []
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    text_content.append(text)
            return "\n".join(text_content)
        except Exception as e:
            raise ValueError(f"Error processing PDF file: {str(e)}")
    
    def _process_docx_file(self, filepath):
        """Process DOCX files"""
        try:
            doc = docx.Document(filepath)
            text_content = []
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            return "\n".join(text_content)
        except Exception as e:
            raise ValueError(f"Error processing DOCX file: {str(e)}")

