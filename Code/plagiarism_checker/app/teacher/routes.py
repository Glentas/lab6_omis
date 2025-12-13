from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Report
from app.teacher import bp
from app.teacher.services import get_all_students, get_student_by_id, get_reports_for_student, get_all_reports

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
    reports = get_reports_for_student(student_id)
    return render_template('teacher/view_student_reports.html', student=student, reports=reports)

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
    # Заглушка: просто подтверждаем
    flash('Оценка выставлена (заглушка)')
    report = Report.query.get_or_404(report_id)
    return redirect(url_for('teacher.student_detail', student_id=report.user_id))

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
    # Заглушка: фильтры не реализованы, просто показываем список
    flash('Фильтры не реализованы в MVP')
    return redirect(url_for('teacher.reports'))

@bp.route('/statistics')
@login_required
def statistics():
    if current_user.role != 'teacher':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    return render_template('teacher/statistics.html')
