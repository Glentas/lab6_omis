from app import login_manager
from flask_login import UserMixin
from app import db

UserRole = ['student', 'teacher', 'admin']


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # student, teacher, admin
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    documents = db.relationship('SourceDocument', back_populates='user')
    reports = db.relationship('Report', back_populates='user')


class SourceDocument(db.Model):
    __tablename__ = 'source_documents'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    # pdf, docx, txt
    format = db.Column(db.String(10), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='documents')
    processed_text = db.relationship(
        'ProcessedText', back_populates='document', uselist=False)


class ProcessedText(db.Model):
    __tablename__ = 'processed_texts'
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey(
        'source_documents.id'), nullable=False)
    extracted_text = db.Column(db.Text)
    # pending, completed, error
    status = db.Column(db.String(20), default='pending')

    document = db.relationship(
        'SourceDocument', back_populates='processed_text')
    checks = db.relationship(
        'PlagiarismCheck', back_populates='processed_text')


class PlagiarismCheck(db.Model):
    __tablename__ = 'plagiarism_checks'
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer, db.ForeignKey(
        'processed_texts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    check_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    uniqueness_percentage = db.Column(db.Float)

    processed_text = db.relationship('ProcessedText', back_populates='checks')
    report = db.relationship('Report', back_populates='check', uselist=False)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    check_id = db.Column(db.Integer, db.ForeignKey(
        'plagiarism_checks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    generated_date = db.Column(
        db.DateTime, default=db.func.current_timestamp())
    uniqueness_percentage = db.Column(db.Float)

    user = db.relationship('User', back_populates='reports')
    check = db.relationship('PlagiarismCheck', back_populates='report')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
