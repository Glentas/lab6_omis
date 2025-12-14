import os
import shutil
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import SourceDocument, Report, ProcessedText, PlagiarismCheck
from app.student import bp
from app.student.services import allowed_file, simulate_preprocessing, simulate_analysis
from config import UPLOAD_FOLDER, DB_FOLDER


@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    return render_template('student/dashboard.html')


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'student':
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
            filepath_db = os.path.join(DB_FOLDER, filename)

            if os.path.exists(filepath):
                flash('Файл с таким именем уже существует!')
                return redirect(request.url)

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
            simulate_analysis(processed_id, current_user.id, filepath)
            flash('Документ загружен. Обработка начата.')

            shutil.copy2(filepath, filepath_db)

            return redirect(url_for('student.analysis_wait', doc_id=doc.id))
        else:
            flash('Неподдерживаемый формат файла')
    return render_template('student/upload.html')


@bp.route('/preprocessing_wait/<int:doc_id>')
@login_required
def preprocessing_wait(doc_id):
    doc = SourceDocument.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        flash('Нет доступа')
        return redirect(url_for('student.dashboard'))
    return render_template('student/preprocessing_wait.html', doc_id=doc_id)


@bp.route('/analysis_wait/<int:doc_id>')
@login_required
def analysis_wait(doc_id):
    doc = SourceDocument.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        flash('Нет доступа')
        return redirect(url_for('student.dashboard'))
    return render_template('student/analysis_wait.html', doc_id=doc_id)


@bp.route('/report_ready/<int:doc_id>')
@login_required
def report_ready(doc_id):
    doc = SourceDocument.query.get_or_404(doc_id)
    if doc.user_id != current_user.id:
        flash('Нет доступа')
        return redirect(url_for('student.dashboard'))
    processed = ProcessedText.query.filter_by(doc_id=doc_id).first()
    if not processed:
        flash('Обработка не завершена')
        return redirect(url_for('student.analysis_wait', doc_id=doc_id))
    check = PlagiarismCheck.query.filter_by(doc_id=processed.id).order_by(
        PlagiarismCheck.check_date.desc()).first()
    if not check:
        flash('Анализ не завершён')
        return redirect(url_for('student.analysis_wait', doc_id=doc_id))
    report = Report.query.filter_by(check_id=check.id).first()
    if not report:
        flash('Отчёт не сформирован')
        return redirect(url_for('student.analysis_wait', doc_id=doc_id))
    return render_template('student/report_ready.html', report_id=report.id, doc_id=doc_id)


@bp.route('/view_report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('Нет доступа')
        return redirect(url_for('student.dashboard'))
    return render_template('student/view_report.html', report=report)


@bp.route('/export_report/<int:report_id>')
@login_required
def export_report(report_id):
    report = Report.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash('Нет доступа')
        return redirect(url_for('student.dashboard'))
    flash('Экспорт в PDF выполнен (заглушка)')
    return redirect(url_for('student.view_report', report_id=report_id))


@bp.route('/history')
@login_required
def history():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    reports = Report.query.filter_by(user_id=current_user.id).order_by(
        Report.generated_date.desc()).all()
    return render_template('student/history.html', reports=reports)
