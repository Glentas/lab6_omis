import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Report, SourceDocument
from app.teacher import bp
from app.teacher.services import get_all_students, get_student_by_id, get_reports_for_student, get_all_reports
from app.teacher.services import allowed_file, simulate_preprocessing, simulate_analysis
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER


@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('auth.login'))
    return render_template('teacher/dashboard.html')


@bp.route('/manage_students')
@login_required
def manage_students():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    return render_template('teacher/manage_students.html')


@bp.route('/student_list')
@login_required
def student_list():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    students = get_all_students()
    return render_template('teacher/student_list.html', students=students)


@bp.route('/student_detail/<int:student_id>')
@login_required
def student_detail(student_id):
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    student = get_student_by_id(student_id)
    if not student:
        flash('Студент не найден')
        return redirect(url_for('teacher.student_list'))
    return render_template('teacher/student_detail.html', student=student)


@bp.route('/view_student_reports/<int:student_id>')
@login_required
def view_student_reports(student_id):
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    student = get_student_by_id(student_id)
    if not student:
        flash('Студент не найден')
        return redirect(url_for('teacher.student_list'))
    reports2 = get_reports_for_student(student_id)
    return render_template('teacher/view_student_reports.html', student=student, reports=reports2)


@bp.route('/view_report/<int:report_id>')
@login_required
def view_report(report_id):
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    report = Report.query.get_or_404(report_id)
    return render_template('teacher/view_report.html', report=report)


@bp.route('/grade_work/<int:report_id>')
@login_required
def grade_work(report_id):
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    report = Report.query.get_or_404(report_id)
    return render_template('teacher/grade_work.html', report=report)


@bp.route('/submit_grade/<int:report_id>', methods=['POST'])
@login_required
def submit_grade(report_id):
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))

    flash('Оценка выставлена (заглушка)')
    report = Report.query.get_or_404(report_id)
    return redirect(url_for('teacher.student_detail', student_id=report.user_id))


@bp.route('/upload_document', methods=['GET', 'POST'])
@login_required
def upload_document():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            doc = SourceDocument(
                filename=filename,
                format=filename.rsplit('.', 1)[1].lower(),
                size=os.path.getsize(filepath),
                user_id=current_user.id
            )
            db.session.add(doc)
            db.session.commit()

            processed_id = simulate_preprocessing(doc)
            simulate_analysis(processed_id, current_user.id)

            flash('Документ обработан. Отчёт готов.')
            report = Report.query.filter_by(user_id=current_user.id).order_by(
                Report.generated_date.desc()).first()
            return redirect(url_for('teacher.view_report', report_id=report.id))
        else:
            flash('Неподдерживаемый формат файла')
    return render_template('teacher/upload_document.html')


@bp.route('/reports')
@login_required
def reports():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    all_reports = get_all_reports()
    return render_template('teacher/reports.html', reports=all_reports)


@bp.route('/filter_reports')
@login_required
def filter_reports():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    flash('Фильтры не реализованы в MVP')
    return redirect(url_for('teacher.reports'))


@bp.route('/statistics')
@login_required
def statistics():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    return render_template('teacher/statistics.html')
