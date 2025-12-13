from app.models import User, Report, SourceDocument

def get_all_students():
    return User.query.filter_by(role='student').all()

def get_student_by_id(student_id):
    return User.query.filter_by(id=student_id, role='student').first()

def get_reports_for_student(student_id):
    return Report.query.filter_by(user_id=student_id).order_by(Report.generated_date.desc()).all()

def get_all_reports():
    return Report.query.order_by(Report.generated_date.desc()).all()
