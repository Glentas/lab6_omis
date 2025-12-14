import time
import random
from app import db
from app.models import SourceDocument, ProcessedText, PlagiarismCheck, Report

SUPPORTED_FORMATS = {'txt', 'pdf', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in SUPPORTED_FORMATS


def simulate_preprocessing(doc: SourceDocument):
    """Имитация предобработки: извлекаем текст (заглушка)"""
    time.sleep(1)
    processed = ProcessedText(
        doc_id=doc.id,
        extracted_text="Заглушенный обработанный текст...",
        status='completed'
    )
    db.session.add(processed)
    db.session.commit()
    return processed.id


def simulate_analysis(processed_text_id: int, user_id: int):
    """Имитация анализа: генерация случайной уникальности"""
    time.sleep(2)
    uniqueness = round(random.uniform(60.0, 99.9), 2)
    check = PlagiarismCheck(
        doc_id=processed_text_id,
        user_id=user_id,
        uniqueness_percentage=uniqueness
    )
    db.session.add(check)
    db.session.commit()

    report = Report(
        check_id=check.id,
        user_id=user_id,
        uniqueness_percentage=uniqueness
    )
    db.session.add(report)
    db.session.commit()
    return report.id
