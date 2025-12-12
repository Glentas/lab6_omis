from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ERROR = "error"


class CheckStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    RTF = "rtf"


# Основные модели данных
class User(BaseModel):
    user_id: str
    name: str
    email: str
    role: UserRole
    registration_date: datetime = Field(default_factory=datetime.now)
    password_hash: Optional[str] = None
    
    class Config:
        from_attributes = True


class SourceDocument(BaseModel):
    doc_id: str
    file_name: str
    format: DocumentFormat
    file_size: int
    upload_date: datetime = Field(default_factory=datetime.now)
    user_id: str
    file_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProcessedText(BaseModel):
    text_id: str
    doc_id: str
    extracted_text: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    processed_date: Optional[datetime] = None
    normalized_text: Optional[str] = None
    
    class Config:
        from_attributes = True


class Source(BaseModel):
    source_id: str
    source_name: str
    author: str
    url: str
    publication_date: Optional[datetime] = None
    category: str = "academic"
    
    class Config:
        from_attributes = True


class Match(BaseModel):
    match_id: str
    check_id: str
    source_id: str
    position_in_text: str
    match_percentage: float
    fragment_context: str
    matched_text: str
    
    class Config:
        from_attributes = True


class PlagiarismCheck(BaseModel):
    check_id: str
    doc_id: str
    user_id: str
    check_date: datetime = Field(default_factory=datetime.now)
    status: CheckStatus = CheckStatus.PENDING
    unique_percentage: float = 0.0
    match_count: int = 0
    
    class Config:
        from_attributes = True


class CheckResult(BaseModel):
    results_id: str
    check_id: str
    matches: List[Match] = []
    uniqueness_score: float = 0.0
    sources: List[Source] = []
    
    class Config:
        from_attributes = True


class Report(BaseModel):
    report_id: str
    check_id: str
    user_id: str
    generated_date: datetime = Field(default_factory=datetime.now)
    unique_percentage: float = 0.0
    match_count: int = 0
    summary: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class Session(BaseModel):
    session_id: str
    user_id: str
    login_time: datetime = Field(default_factory=datetime.now)
    logout_time: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True
