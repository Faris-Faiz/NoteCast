import re
from typing import List, Dict, Any
import PyPDF2
import docx
from PIL import Image
import pytesseract
import io
from config import MAX_TEXT_LENGTH, CHUNK_SIZE

class TextProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content."""
        if not text or not isinstance(text, str):
            return ""
        
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            # Remove special characters but keep basic punctuation
            text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
            # Normalize quotes
            text = re.sub(r'["“”]', '"', text)
            # Normalize apostrophes
            text = re.sub(r'[''′]', "'", text)
            # Fix spacing around punctuation
            text = re.sub(r'\s+([.,!?;:])', r'\1', text)
            return text.strip()
        except Exception as e:
            print(f"Error in clean_text: {e}")
            return text

    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """
        Split text into smaller chunks while preserving sentence boundaries.
        
        Args:
            text (str): Input text to be chunked
            chunk_size (int, optional): Maximum size of each chunk. Defaults to CHUNK_SIZE.
        
        Returns:
            List[str]: List of text chunks
        """
        if not text:
            return []
        
        try:
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                if current_length + sentence_length > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(sentence)
                current_length += sentence_length
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
        except Exception as e:
            print(f"Error in chunk_text: {e}")
            return [text]  # Return original text if chunking fails

    @staticmethod
    def extract_text_from_pdf(file_obj: Any) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return TextProcessor.clean_text(text)
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_obj: Any) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_obj)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return TextProcessor.clean_text(text)
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    @staticmethod
    def extract_text_from_image(file_obj: Any) -> str:
        """Extract text from image using OCR."""
        try:
            image = Image.open(file_obj)
            # Convert image to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            # Perform OCR
            text = pytesseract.image_to_string(image)
            return TextProcessor.clean_text(text)
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")

    @staticmethod
    def validate_text_length(text: str) -> bool:
        """Validate if text length is within acceptable limits."""
        return len(text) <= MAX_TEXT_LENGTH

    @staticmethod
    def extract_structure(text: str) -> Dict[str, Any]:
        """Extract document structure (headings, paragraphs, bullet points)."""
        structure = {
            'headings': [],
            'paragraphs': [],
            'bullet_points': []
        }
        
        try:
            # Extract headings (lines followed by newline and not starting with bullet)
            heading_pattern = r'^(?!\s*[-*•])[A-Z][^\n]+(?:\n|$)'
            structure['headings'] = re.findall(heading_pattern, text, re.MULTILINE)
            
            # Extract bullet points
            bullet_pattern = r'^\s*[-*•]\s*([^\n]+)'
            structure['bullet_points'] = re.findall(bullet_pattern, text, re.MULTILINE)
            
            # Extract paragraphs (text blocks separated by double newline)
            paragraphs = re.split(r'\n\s*\n', text)
            structure['paragraphs'] = [p.strip() for p in paragraphs if p.strip()]
            
        except Exception as e:
            print(f"Error extracting structure: {str(e)}")
            # Return empty structure on error
            return structure
        
        return structure

    @staticmethod
    def format_for_summary(text: str) -> str:
        """Format text for summary generation."""
        try:
            structure = TextProcessor.extract_structure(text)
            formatted_text = ""
            
            # Add headings
            if structure['headings']:
                formatted_text += "Main Topics:\n"
                for heading in structure['headings']:
                    formatted_text += f"- {heading}\n"
                formatted_text += "\n"
            
            # Add bullet points
            if structure['bullet_points']:
                formatted_text += "Key Points:\n"
                for point in structure['bullet_points']:
                    formatted_text += f"• {point}\n"
                formatted_text += "\n"
            
            # Add main content
            formatted_text += "Content:\n"
            for paragraph in structure['paragraphs']:
                if paragraph not in structure['headings']:
                    formatted_text += f"{paragraph}\n\n"
            
            return formatted_text.strip()
        except Exception as e:
            print(f"Error formatting text: {str(e)}")
            return text  # Return original text on error

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect the primary language of the text with improved robustness."""
        if not text:
            return 'unknown'
        
        try:
            # Expanded language detection patterns
            language_patterns = {
                'en': r'\b(the|and|is|in|to|of|a|for|that|this|an|be|have|it|on|at)\b',
                'es': r'\b(el|la|los|las|un|una|unos|unas|y|de|en|con|por|para)\b',
                'fr': r'\b(le|la|les|un|une|des|de|et|dans|sur|pour|avec)\b'
            }
            
            detected_languages = {}
            for lang, pattern in language_patterns.items():
                count = len(re.findall(pattern, text.lower()))
                detected_languages[lang] = count
            
            # Return the language with the most matches, default to 'unknown'
            if detected_languages:
                return max(detected_languages, key=detected_languages.get)
            return 'unknown'
        except Exception as e:
            print(f"Error detecting language: {e}")
            return 'unknown'

    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract key terms and phrases from the text with improved extraction."""
        if not text:
            return []
        
        try:
            # More comprehensive stop words list
            common_words = {
                'the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'that', 'this', 
                'an', 'be', 'have', 'it', 'on', 'at', 'are', 'was', 'were', 'will'
            }
            
            # Tokenize and clean words
            words = re.findall(r'\b\w+\b', text.lower())
            keywords = [word for word in words if word not in common_words and len(word) > 3]
            
            # Count frequency with additional weight for unique words
            keyword_freq = {}
            for word in keywords:
                keyword_freq[word] = keyword_freq.get(word, 0) + 1
            
            # Sort by frequency and uniqueness
            sorted_keywords = sorted(
                keyword_freq.items(), 
                key=lambda x: (x[1], len(x[0])), 
                reverse=True
            )
            
            return [word for word, freq in sorted_keywords[:max_keywords]]
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return []
