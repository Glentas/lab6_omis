from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User
from app.admin import bp
from app.admin.services import get_all_users, get_user_by_id, create_user, update_user

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Доступ запрещён')
        return redirect(url_for('auth.login'))
    return render_template('admin/dashboard.html')

# --- Управление пользователями ---
@bp.route('/user_management')
@login_required
def user_management():
    return render_template('admin/user_management.html')

@bp.route('/user_list')
@login_required
def user_list():
    users = get_all_users()
    return render_template('admin/user_list.html', users=users)

@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        if not all([name, email, role, password]):
            flash('Все поля обязательны')
        elif User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует')
        else:
            create_user(name, email, role, password)
            flash('Пользователь добавлен')
            return redirect(url_for('admin.user_list'))
    return render_template('admin/add_user.html')

@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash('Пользователь не найден')
        return redirect(url_for('admin.user_list'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        if not all([name, email, role]):
            flash('Все поля обязательны')
        else:
            # Проверка уникальности email (простая)
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != user_id:
                flash('Email уже используется другим пользователем')
            else:
                update_user(user_id, name, email, role)
                flash('Пользователь обновлён')
                return redirect(url_for('admin.user_list'))
    return render_template('admin/edit_user.html', user=user)

# --- Системные настройки (заглушки) ---
@bp.route('/system_settings')
@login_required
def system_settings():
    return render_template('admin/system_settings.html')

@bp.route('/security_settings')
@login_required
def security_settings():
    flash('Безопасность: настройки открыты (заглушка)')
    return render_template('admin/security_settings.html')

@bp.route('/algorithm_settings')
@login_required
def algorithm_settings():
    flash('Алгоритмы: настройки не реализованы')
    return render_template('admin/algorithm_settings.html')

@bp.route('/database_settings')
@login_required
def database_settings():
    flash('Параметры БД: только чтение в MVP')
    return render_template('admin/database_settings.html')

# --- Управление БД ---
@bp.route('/database_management')
@login_required
def database_management():
    return render_template('admin/database_management.html')

@bp.route('/backup_db')
@login_required
def backup_db():
    flash('Резервная копия успешно создана (заглушка)')
    return redirect(url_for('admin.database_management'))

@bp.route('/optimize_db')
@login_required
def optimize_db():
    flash('Оптимизация завершена (заглушка)')
    return redirect(url_for('admin.database_management'))

@bp.route('/update_sources')
@login_required
def update_sources():
    flash('Обновление источников запущено (заглушка)')
    return redirect(url_for('admin.database_management'))

# --- Мониторинг и аудит ---
@bp.route('/monitoring')
@login_required
def monitoring():
    return render_template('admin/monitoring.html')

@bp.route('/system_stats')
@login_required
def system_stats():
    return render_template('admin/system_stats.html', stats={
        'cpu': '23%',
        'ram': '1.2 GB / 8 GB',
        'active_users': '5',
        'current_checks': '2'
    })

@bp.route('/alerts_list')
@login_required
def alerts_list():
    alerts = [
        {'time': '2025-12-12 14:30', 'type': 'Warning', 'msg': 'Низкая уникальность у студента #102'},
        {'time': '2025-12-13 09:15', 'type': 'Info', 'msg': 'Завершена обработка документа #45'}
    ]
    return render_template('admin/alerts_list.html', alerts=alerts)

@bp.route('/audit_log')
@login_required
def audit_log():
    logs = [
        {'user': 'admin', 'action': 'login', 'time': '2025-12-13 08:00'},
        {'user': 'teacher@example.com', 'action': 'graded report #12', 'time': '2025-12-13 10:05'},
    ]
    return render_template('admin/audit_log.html', logs=logs)

@bp.route('/log_viewer')
@login_required
def log_viewer():
    return render_template('admin/log_viewer.html')

@bp.route('/filter_log')
@login_required
def filter_log():
    flash('Фильтр применён (заглушка)')
    return redirect(url_for('admin.log_viewer'))
