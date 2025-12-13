#!/bin/bash

# Название проекта
PROJECT_NAME="plagiarism_checker"

echo "Создание структуры проекта: $PROJECT_NAME"

mkdir -p "$PROJECT_NAME"/{app/{auth,student,teacher,admin,templates/{student,teacher,admin}},migrations}

# Создание файлов в корне
touch "$PROJECT_NAME"/{requirements.txt,config.py,run.py}

# Создание файлов в app/
touch "$PROJECT_NAME"/app/__init__.py
touch "$PROJECT_NAME"/app/models.py

# Blueprint: auth
touch "$PROJECT_NAME"/app/auth/{__init__.py,routes.py,utils.py}

# Blueprint: student
touch "$PROJECT_NAME"/app/student/{__init__.py,routes.py,services.py}

# Blueprint: teacher
touch "$PROJECT_NAME"/app/teacher/{__init__.py,routes.py,services.py}

# Blueprint: admin
touch "$PROJECT_NAME"/app/admin/{__init__.py,routes.py,services.py}

# Шаблоны: base + login
touch "$PROJECT_NAME"/app/templates/{base.html,login.html}

# Шаблоны: студент
for f in dashboard.html upload.html preprocessing_wait.html analysis_wait.html report_ready.html view_report.html export_report.html history.html; do
  touch "$PROJECT_NAME"/app/templates/student/"$f"
done

# Шаблоны: преподаватель
for f in dashboard.html manage_students.html student_list.html student_detail.html view_student_reports.html view_report.html grade_work.html submit_grade.html reports.html filter_reports.html statistics.html; do
  touch "$PROJECT_NAME"/app/templates/teacher/"$f"
done

# Шаблоны: администратор
for f in dashboard.html user_management.html user_list.html add_user.html edit_user.html system_settings.html security_settings.html algorithm_settings.html database_settings.html database_management.html update_sources.html sync_progress.html backup_db.html backup_progress.html optimize_db.html monitoring.html system_stats.html alerts_list.html audit_log.html log_viewer.html filter_log.html; do
  touch "$PROJECT_NAME"/app/templates/admin/"$f"
done

echo "✅ Структура проекта создана."
echo "Перейдите в папку: cd $PROJECT_NAME"
