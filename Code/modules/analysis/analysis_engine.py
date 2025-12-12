import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import streamlit as st

from app.core.models import (
    SourceDocument, ProcessedText, ProcessingStatus, 
    DocumentFormat, PlagiarismCheck, CheckStatus
)
from app.storage.json_storage import StorageManager
from app.utils.file_processor import FileProcessor
from app.utils.text_utils import TextProcessor


class DocumentManager:
    """Менеджер документов - обработка и управление документами"""
    
    def __init__(self, storage: StorageManager):
        self.storage = storage
        self.file_processor = FileProcessor()
        self.text_processor = TextProcessor()
    
    def upload_document(self, uploaded_file, user_id: str) -> Dict[str, Any]:
        """Загрузка документа в систему"""
        try:
            # Сохранение файла
            file_path = FileProcessor.save_uploaded_file(uploaded_file, user_id)
            
            # Получение информации о файле
            file_name, file_format, file_size = FileProcessor.get_file_info(file_path)
            
            # Создание записи документа
            doc_id = str(uuid.uuid4())
            document_data = {
                "doc_id": doc_id,
                "file_name": file_name,
                "format": file_format.value,
                "file_size": file_size,
                "upload_date": datetime.now().isoformat(),
                "user_id": user_id,
                "file_path": str(file_path)
            }
            
            self.storage.documents.create("documents", document_data, doc_id)
            
            return {
                "success": True,
                "doc_id": doc_id,
                "file_name": file_name,
                "message": "Документ успешно загружен"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при загрузке документа: {str(e)}"
            }
    
    def process_document(self, doc_id: str) -> Dict[str, Any]:
        """Обработка документа: извлечение и нормализация текста"""
        try:
            # Получение документа
            document = self.storage.documents.read("documents", doc_id)
            if not document:
                return {"success": False, "message": "Документ не найден"}
            
            file_path = Path(document["file_path"])
            file_format = DocumentFormat(document["format"])
            
            # Извлечение текста
            extracted_text = self.file_processor.extract_text(file_path, file_format)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                return {"success": False, "message": "Не удалось извлечь текст из документа"}
            
            # Нормализация текста
            normalized_text = self.text_processor.normalize_text(extracted_text)
            
            # Создание записи обработанного текста
            text_id = str(uuid.uuid4())
            processed_text_data = {
                "text_id": text_id,
                "doc_id": doc_id,
                "extracted_text": extracted_text,
                "normalized_text": normalized_text,
                "status": ProcessingStatus.COMPLETED.value,
                "processed_date": datetime.now().isoformat()
            }
            
            self.storage.processed_texts.create("processed_texts", processed_text_data, text_id)
            
            # Обновление статуса документа
            self.storage.documents.update("documents", doc_id, {
                "processed": True,
                "processed_date": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "text_id": text_id,
                "extracted_text": extracted_text,
                "normalized_text": normalized_text,
                "text_length": len(extracted_text),
                "word_count": len(extracted_text.split())
            }
            
        except Exception as e:
            # Обновление статуса на ошибку
            error_text_id = str(uuid.uuid4())
            error_text_data = {
                "text_id": error_text_id,
                "doc_id": doc_id,
                "extracted_text": "",
                "status": ProcessingStatus.ERROR.value,
                "processed_date": datetime.now().isoformat(),
                "error_message": str(e)
            }
            
            self.storage.processed_texts.create("processed_texts", error_text_data, error_text_id)
            
            return {
                "success": False,
                "message": f"Ошибка при обработке документа: {str(e)}"
            }
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение списка документов пользователя"""
        documents = self.storage.documents.find("documents", user_id=user_id)
        
        # Добавление информации об обработке
        for doc in documents:
            doc_id = doc["doc_id"]
            processed_texts = self.storage.processed_texts.find("processed_texts", doc_id=doc_id)
            
            if processed_texts:
                doc["processed"] = True
                doc["processed_date"] = processed_texts[0].get("processed_date")
                doc["status"] = processed_texts[0].get("status")
            else:
                doc["processed"] = False
                doc["status"] = ProcessingStatus.PENDING.value
        
        return sorted(documents, key=lambda x: x.get("upload_date", ""), reverse=True)
    
    def get_document_details(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Получение детальной информации о документе"""
        document = self.storage.documents.read("documents", doc_id)
        if not document:
            return None
        
        # Поиск обработанного текста
        processed_texts = self.storage.processed_texts.find("processed_texts", doc_id=doc_id)
        if processed_texts:
            document["processed_text"] = processed_texts[0]
        
        # Поиск проверок
        checks = self.storage.checks.find("checks", doc_id=doc_id)
        document["checks"] = checks
        
        return document
    
    def delete_document(self, doc_id: str, user_id: str) -> bool:
        """Удаление документа"""
        document = self.storage.documents.read("documents", doc_id)
        
        if not document or document.get("user_id") != user_id:
            return False
        
        try:
            # Удаление файла
            file_path = document.get("file_path")
            if file_path:
                Path(file_path).unlink(missing_ok=True)
            
            # Удаление связанных записей
            processed_texts = self.storage.processed_texts.find("processed_texts", doc_id=doc_id)
            for pt in processed_texts:
                self.storage.processed_texts.delete("processed_texts", pt["text_id"])
            
            checks = self.storage.checks.find("checks", doc_id=doc_id)
            for check in checks:
                self.storage.checks.delete("checks", check["check_id"])
            
            # Удаление документа
            self.storage.documents.delete("documents", doc_id)
            
            return True
            
        except Exception as e:
            st.error(f"Ошибка при удалении документа: {str(e)}")
            return False
