import PyPDF2
from docx import Document
from pathlib import Path
import tempfile
from typing import Optional, Tuple
import io

from app.core.config import AppConfig
from app.core.models import DocumentFormat


class FileProcessor:
    """Обработчик файлов различных форматов"""
    
    @staticmethod
    def extract_text(file_path: Path, file_format: DocumentFormat) -> str:
        """Извлечение текста из файла"""
        try:
            if file_format == DocumentFormat.PDF:
                return FileProcessor._extract_from_pdf(file_path)
            elif file_format in [DocumentFormat.DOCX, DocumentFormat.DOC]:
                return FileProcessor._extract_from_docx(file_path)
            elif file_format == DocumentFormat.TXT:
                return FileProcessor._extract_from_txt(file_path)
            elif file_format == DocumentFormat.RTF:
                return FileProcessor._extract_from_rtf(file_path)
            else:
                raise ValueError(f"Unsupported format: {file_format}")
        except Exception as e:
            raise Exception(f"Error extracting text from {file_path}: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file_path: Path) -> str:
        """Извлечение текста из PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def _extract_from_docx(file_path: Path) -> str:
        """Извлечение текста из DOCX"""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    
    @staticmethod
    def _extract_from_txt(file_path: Path) -> str:
        """Извлечение текста из TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    @staticmethod
    def _extract_from_rtf(file_path: Path) -> str:
        """Извлечение текста из RTF"""
        # Простая реализация для RTF - можно заменить на более продвинутую
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            # Удаляем RTF-теги
            import re
            text = re.sub(r'\\[a-z]+[0-9]*', '', content)
            text = re.sub(r'\{.*?\}', '', text)
            return text.strip()
    
    @staticmethod
    def get_file_info(file_path: Path) -> Tuple[str, DocumentFormat, int]:
        """Получение информации о файле"""
        file_name = file_path.name
        file_size = file_path.stat().st_size
        
        # Определение формата
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            format_type = DocumentFormat.PDF
        elif suffix == ".docx":
            format_type = DocumentFormat.DOCX
        elif suffix == ".doc":
            format_type = DocumentFormat.DOC
        elif suffix == ".txt":
            format_type = DocumentFormat.TXT
        elif suffix == ".rtf":
            format_type = DocumentFormat.RTF
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        return file_name, format_type, file_size
    
    @staticmethod
    def save_uploaded_file(uploaded_file, user_id: str) -> Path:
        """Сохранение загруженного файла"""
        # Создание уникального имени файла
        import uuid
        file_ext = Path(uploaded_file.name).suffix
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_ext}"
        save_path = AppConfig.UPLOAD_DIR / unique_filename
        
        # Сохранение файла
        with open(save_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return save_path
