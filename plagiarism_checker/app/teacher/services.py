from app.models import User, Report, SourceDocument
from app import db
from app.models import ProcessedText, PlagiarismCheck
from app.core.plagiarism_check import check_document_originality as cdo
from config import DB_FOLDER


SUPPORTED_FORMATS = {'txt', 'pdf', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in SUPPORTED_FORMATS


def simulate_preprocessing(doc: SourceDocument):
    processed = ProcessedText(
        doc_id=doc.id,
        extracted_text="Заглушенный текст (преподаватель)",
        status='completed'
    )
    db.session.add(processed)
    db.session.commit()
    return processed.id


def simulate_analysis(processed_text_id: int, user_id: int, filepath):
    uniqueness = cdo(filepath, DB_FOLDER)
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


def get_all_students():
    return User.query.filter_by(role='student').all()


def get_student_by_id(student_id):
    return User.query.filter_by(id=student_id, role='student').first()


def get_reports_for_student(student_id):
    return Report.query.filter_by(user_id=student_id).order_by(Report.generated_date.desc()).all()


def get_all_reports():
    return Report.query.order_by(Report.generated_date.desc()).all()
