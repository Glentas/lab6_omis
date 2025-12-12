import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import random
import time
import threading
import os
import json
import datetime
import hashlib
import re
import string
from collections import defaultdict
from itertools import product
import sys
import inspect

# Глобальные переменные везде, потому что почему нет
global_var_1 = None
global_var_2 = None
global_var_3 = None
global_list = []
global_dict = {}
user_data = None
documents = {}
analysis_results = {}
reports = {}
user_actions = []
system_log = []

# Классы, которые нарушают все принципы SOLID


class Everything:
    def __init__(self):
        self.users = []
        self.documents = []
        self.analyses = []
        self.reports = []
        self.settings = {}
        self.logs = []
        self.cache = {}
        self.connections = []

    def do_everything(self, user_id, doc_id, action, param1, param2, param3, param4=None):
        # Нарушаем Single Responsibility Principle
        # Этот метод делает все: пользователей, документы, анализ, логирование

        # Генерируем случайные данные
        rand = random.randint(1, 100)

        # Логируем
        self.logs.append(
            f"{datetime.datetime.now()}: User {user_id} did {action}")

        # Обновляем кэш
        self.cache[f"{user_id}_{doc_id}"] = rand

        # Если есть param4, делаем что-то еще
        if param4:
            for i in range(10):
                self.users.append(f"user_{i}")

        # Возвращаем что-нибудь
        return rand, self.logs[-1], list(self.cache.keys())[:5] if self.cache else []

    def analyze_document(self, text, user, options={}, extra_params=None):
        # Нарушаем Open/Closed Principle - жестко закодированные условия
        if "mode" in options and options["mode"] == "fast":
            result = random.random() * 50
        elif "mode" in options and options["mode"] == "deep":
            result = random.random() * 100
        else:
            result = random.random() * 80

        # Добавляем побочные эффекты
        self.documents.append(text[:100])
        self.analyses.append(result)

        # Меняем состояние объекта непредсказуемо
        if random.random() > 0.5:
            self.settings["last_analysis"] = datetime.datetime.now()
        else:
            self.settings["last_user"] = user

        return {"score": result, "matches": random.randint(0, 20)}

    def create_report(self, analysis_result, user, format="html", style=None):
        # Нарушаем Interface Segregation - слишком много параметров
        report_id = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        report = {
            "id": report_id,
            "user": user,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": analysis_result["score"] if isinstance(analysis_result, dict) else analysis_result,
            "content": f"Report {report_id} for user {user}"
        }

        # Сохраняем в разных местах
        self.reports.append(report)
        if hasattr(self, 'reports_dict'):
            self.reports_dict[report_id] = report
        else:
            self.reports_dict = {report_id: report}

        # Побочный эффект - меняем глобальную переменную
        global global_list
        global_list.append(report_id)

        return report

# Еще один класс, который делает слишком много


class SystemManager:
    def __init__(self):
        self.everything = Everything()
        self.config = self.load_config()
        self.users = self.load_users()
        self.is_running = False
        self.threads = []

    def load_config(self):
        # Хардкодим конфигурацию
        return {
            "database": "localhost:5432/mydb",
            "cache_size": 1000,
            "timeout": 30,
            "modes": ["fast", "deep", "normal"],
            "formats": ["pdf", "docx", "txt"],
            "version": "1.0.0"
        }

    def load_users(self):
        # Нарушаем Dependency Inversion - создаем зависимости внутри метода
        users = {
            "admin": {"password": "admin123", "role": "admin", "permissions": ["all"]},
            "teacher": {"password": "teacher123", "role": "teacher", "permissions": ["upload", "analyze", "view_reports"]},
            "student": {"password": "student123", "role": "student", "permissions": ["upload", "view_own_reports"]}
        }

        # Добавляем случайных пользователей
        for i in range(5):
            users[f"user{i}"] = {"password": f"pass{i}",
                                 "role": "student", "permissions": ["upload"]}

        return users

    def validate_user(self, username, password):
        # Простая валидация с побочными эффектами
        if username in self.users and self.users[username]["password"] == password:
            # Логируем
            self.everything.logs.append(f"User {username} logged in")

            # Меняем конфиг
            if username == "admin":
                self.config["current_user"] = username

            return True, self.users[username]["role"]
        return False, None

    def process_document(self, filepath, username, options={}):
        # Нарушаем DRY - код дублируется
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            with open(filepath, 'r') as f:
                content = f.read()

        # Анализируем
        result = self.everything.analyze_document(content, username, options)

        # Создаем отчет
        report = self.everything.create_report(result, username)

        # Логируем
        self.everything.logs.append(
            f"Document {filepath} processed for {username}")

        # Сохраняем в глобальные переменные
        global documents, analysis_results, reports
        doc_id = hashlib.md5(filepath.encode()).hexdigest()[:8]
        documents[doc_id] = {"path": filepath,
                             "user": username, "content": content[:500]}
        analysis_results[doc_id] = result
        reports[doc_id] = report

        return result, report

    def get_random_message(self):
        # Список сообщений, которые выводятся каждые 5 секунд
        messages = [
            "Я - Леонард, чем могу помочь?",
            "Никита Владимирович",
            "Извини, я пока не знаю, как на это ответить.",
            "Че за хуйня?",
            "ГАТ",
            "Твоя оценка за ЛР №3 дисциплины 'Объектное моделирование интеллектуальных систем' составляет 6 баллов",
            "Я не смог определить, по лабораторной работе какой дисциплины ты хочешь узнать оценку.",
            "Мне нужна помощь"
        ]
        return random.choice(messages)

# Ужасный GUI на Tkinter


class UglyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Плагиат-Детектор 3000 (Ужасная Версия)")
        self.root.geometry("1200x700")

        self.system = SystemManager()
        self.current_user = None
        self.current_role = None

        # Нарушаем все принципы UI/UX
        self.setup_ui()

        # Запускаем поток для сообщений
        self.message_thread = threading.Thread(
            target=self.show_random_messages)
        self.message_thread.daemon = True
        self.message_thread.start()

    def setup_ui(self):
        # Ужасная цветовая схема
        colors = ["#FF0000", "#00FF00", "#0000FF",
                  "#FFFF00", "#FF00FF", "#00FFFF"]
        bg_color = random.choice(colors)
        self.root.configure(bg=bg_color)

        # Создаем все виджеты в одном методе
        self.create_login_frame()
        self.create_main_frame()
        self.create_analysis_frame()
        self.create_report_frame()
        self.create_log_frame()
        self.create_status_frame()

        # Показываем только логин сначала
        self.show_frame("login")

    def create_login_frame(self):
        # Ужасный фрейм логина
        self.login_frame = tk.Frame(
            self.root, bg="#FFCCCC", bd=10, relief="ridge")

        # Кривые надписи
        tk.Label(self.login_frame,
                 text="ВОЙТИ В СИСТЕМУ",
                 font=("Comic Sans MS", 24, "bold"),
                 fg="#FF0000",
                 bg="#FFCCCC").pack(pady=20)

        # Поля ввода
        tk.Label(self.login_frame, text="Логин:",
                 font=("Arial", 14), bg="#FFCCCC").pack()
        self.username_entry = tk.Entry(
            self.login_frame, font=("Arial", 14), width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "admin")

        tk.Label(self.login_frame, text="Пароль:",
                 font=("Arial", 14), bg="#FFCCCC").pack()
        self.password_entry = tk.Entry(
            self.login_frame, font=("Arial", 14), width=30, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "admin123")

        # Кнопка входа
        tk.Button(self.login_frame,
                  text="ВОЙТИ",
                  font=("Arial", 16, "bold"),
                  bg="#00FF00",
                  fg="#000000",
                  command=self.login,
                  width=20,
                  height=2).pack(pady=20)

        # Случайная информация
        tk.Label(self.login_frame,
                 text="Система обнаружения плагиата v1.0\nНарушение всех принципов ООП",
                 font=("Courier", 10),
                 bg="#FFCCCC",
                 fg="#0000FF").pack(pady=10)

    def create_main_frame(self):
        # Главный фрейм с навигацией
        self.main_frame = tk.Frame(self.root, bg="#CCCCFF")

        # Ужасное меню
        menu_frame = tk.Frame(self.main_frame, bg="#FF9900", height=50)
        menu_frame.pack(fill="x", pady=5)

        buttons = [
            ("Анализ", self.show_analysis),
            ("Отчеты", self.show_reports),
            ("Логи", self.show_logs),
            ("Настройки", self.show_settings),
            ("Выйти", self.logout)
        ]

        for i, (text, command) in enumerate(buttons):
            color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
            tk.Button(menu_frame,
                      text=text,
                      command=command,
                      bg=color,
                      fg="white",
                      font=("Arial", 12)).pack(side="left", padx=5, pady=5)

        # Область контента
        self.content_frame = tk.Frame(self.main_frame, bg="#FFFFFF")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_analysis_frame(self):
        # Фрейм анализа
        self.analysis_frame = tk.Frame(self.content_frame, bg="#EEEEEE")

        tk.Label(self.analysis_frame,
                 text="АНАЛИЗ ДОКУМЕНТОВ",
                 font=("Arial", 18, "bold"),
                 bg="#EEEEEE").pack(pady=10)

        # Выбор файла
        file_frame = tk.Frame(self.analysis_frame, bg="#EEEEEE")
        file_frame.pack(pady=10)

        tk.Label(file_frame, text="Файл:", font=(
            "Arial", 12), bg="#EEEEEE").pack(side="left")
        self.file_path = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_path, width=50,
                 font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(file_frame, text="Выбрать",
                  command=self.select_file, bg="#66CCFF").pack(side="left")

        # Опции анализа
        options_frame = tk.Frame(self.analysis_frame, bg="#EEEEEE")
        options_frame.pack(pady=10)

        tk.Label(options_frame, text="Режим анализа:", font=(
            "Arial", 12), bg="#EEEEEE").pack(side="left")
        self.analysis_mode = tk.StringVar(value="normal")

        modes = [("Быстрый", "fast"), ("Нормальный",
                                       "normal"), ("Глубокий", "deep")]
        for text, value in modes:
            tk.Radiobutton(options_frame,
                           text=text,
                           variable=self.analysis_mode,
                           value=value,
                           bg="#EEEEEE").pack(side="left", padx=5)

        # Кнопка анализа
        tk.Button(self.analysis_frame,
                  text="ЗАПУСТИТЬ АНАЛИЗ",
                  font=("Arial", 14, "bold"),
                  bg="#FF6666",
                  fg="white",
                  command=self.run_analysis,
                  width=20).pack(pady=20)

        # Область результатов
        self.result_text = scrolledtext.ScrolledText(self.analysis_frame,
                                                     height=15,
                                                     width=80,
                                                     font=("Courier", 10))
        self.result_text.pack(pady=10)

    def create_report_frame(self):
        # Фрейм отчетов
        self.report_frame = tk.Frame(self.content_frame, bg="#EEFFEE")

        tk.Label(self.report_frame,
                 text="ОТЧЕТЫ",
                 font=("Arial", 18, "bold"),
                 bg="#EEFFEE").pack(pady=10)

        # Список отчетов
        list_frame = tk.Frame(self.report_frame, bg="#EEFFEE")
        list_frame.pack(pady=10)

        tk.Label(list_frame, text="Отчеты:", font=(
            "Arial", 12), bg="#EEFFEE").pack(side="left")

        self.report_listbox = tk.Listbox(
            list_frame, width=50, height=10, font=("Arial", 10))
        self.report_listbox.pack(side="left", padx=5)

        tk.Button(list_frame,
                  text="Обновить",
                  command=self.update_reports,
                  bg="#99FF99").pack(side="left", padx=5)

        # Просмотр отчета
        view_frame = tk.Frame(self.report_frame, bg="#EEFFEE")
        view_frame.pack(pady=10)

        tk.Button(view_frame,
                  text="Просмотреть отчет",
                  command=self.view_report,
                  bg="#66CCFF").pack(side="left", padx=5)

        tk.Button(view_frame,
                  text="Экспорт",
                  command=self.export_report,
                  bg="#FFCC66").pack(side="left", padx=5)

        # Текст отчета
        self.report_text = scrolledtext.ScrolledText(self.report_frame,
                                                     height=15,
                                                     width=80,
                                                     font=("Courier", 10))
        self.report_text.pack(pady=10)

    def create_log_frame(self):
        # Фрейм логов
        self.log_frame = tk.Frame(self.content_frame, bg="#FFFFCC")

        tk.Label(self.log_frame,
                 text="СИСТЕМНЫЕ ЛОГИ",
                 font=("Arial", 18, "bold"),
                 bg="#FFFFCC").pack(pady=10)

        # Логи
        self.log_text = scrolledtext.ScrolledText(self.log_frame,
                                                  height=20,
                                                  width=90,
                                                  font=("Courier", 9))
        self.log_text.pack(pady=10)

        tk.Button(self.log_frame,
                  text="Обновить логи",
                  command=self.update_logs,
                  bg="#FFCC99").pack(pady=5)

    def create_status_frame(self):
        # Статус бар
        self.status_frame = tk.Frame(self.root, bg="#333333", height=30)
        self.status_frame.pack(side="bottom", fill="x")

        self.status_label = tk.Label(self.status_frame,
                                     text="Готов к работе",
                                     fg="white",
                                     bg="#333333",
                                     font=("Arial", 10))
        self.status_label.pack(side="left", padx=10)

        # Текущий пользователь
        self.user_label = tk.Label(self.status_frame,
                                   text="Пользователь: Не авторизован",
                                   fg="white",
                                   bg="#333333",
                                   font=("Arial", 10))
        self.user_label.pack(side="right", padx=10)

    def show_frame(self, frame_name):
        # Показать нужный фрейм
        frames = {
            "login": self.login_frame,
            "main": self.main_frame
        }

        for frame in frames.values():
            frame.pack_forget()

        if frame_name in frames:
            frames[frame_name].pack(fill="both", expand=True)

    def show_content(self, content_name):
        # Показать контент
        contents = {
            "analysis": self.analysis_frame,
            "reports": self.report_frame,
            "logs": self.log_frame
        }

        for widget in self.content_frame.winfo_children():
            widget.pack_forget()

        if content_name in contents:
            contents[content_name].pack(fill="both", expand=True)

    def login(self):
        # Логин пользователя
        username = self.username_entry.get()
        password = self.password_entry.get()

        valid, role = self.system.validate_user(username, password)

        if valid:
            self.current_user = username
            self.current_role = role

            # Обновляем статус
            self.user_label.config(text=f"Пользователь: {username} ({role})")
            self.status_label.config(text="Авторизация успешна")

            # Показываем главный экран
            self.show_frame("main")
            self.show_content("analysis")

            # Логируем
            messagebox.showinfo("Успех", f"Добро пожаловать, {username}!")
        else:
            self.status_label.config(text="Ошибка авторизации")
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

            # Меняем цвет для ошибки
            self.login_frame.config(bg="#FF9999")

    def logout(self):
        # Выход
        self.current_user = None
        self.current_role = None
        self.user_label.config(text="Пользователь: Не авторизован")
        self.show_frame("login")
        self.status_label.config(text="Выход выполнен")

    def select_file(self):
        # Выбор файла
        filepath = filedialog.askopenfilename(
            title="Выберите документ",
            filetypes=[("Текстовые файлы", "*.txt;*.docx;*.pdf"),
                       ("Все файлы", "*.*")]
        )

        if filepath:
            self.file_path.set(filepath)
            self.status_label.config(
                text=f"Выбран файл: {os.path.basename(filepath)}")

    def run_analysis(self):
        # Запуск анализа
        filepath = self.file_path.get()

        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Ошибка", "Файл не выбран или не существует")
            return

        # Показываем статус
        self.status_label.config(text="Анализ запущен...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Анализ начат...\n")

        # Запускаем в отдельном потоке (плохая реализация)
        def analyze():
            try:
                options = {"mode": self.analysis_mode.get()}

                # Вызываем метод с кучей параметров
                result, report = self.system.process_document(
                    filepath, self.current_user, options)

                # Выводим результат
                self.result_text.insert(
                    tk.END, f"\n=== РЕЗУЛЬТАТЫ АНАЛИЗА ===\n")
                self.result_text.insert(
                    tk.END, f"Уникальность: {result.get('score', 0):.2f}%\n")
                self.result_text.insert(
                    tk.END, f"Найдено совпадений: {result.get('matches', 0)}\n")
                self.result_text.insert(
                    tk.END, f"ID отчета: {report.get('id', 'N/A')}\n")
                self.result_text.insert(
                    tk.END, f"Дата: {report.get('date', 'N/A')}\n")

                # Обновляем статус
                self.status_label.config(
                    text=f"Анализ завершен. Уникальность: {result.get('score', 0):.2f}%")

                # Обновляем список отчетов
                self.update_reports()

            except Exception as e:
                self.result_text.insert(tk.END, f"\nОШИБКА: {str(e)}")
                self.status_label.config(text="Ошибка при анализе")

        # Запускаем поток (без правильного управления)
        thread = threading.Thread(target=analyze)
        thread.daemon = True
        thread.start()

    def update_reports(self):
        # Обновление списка отчетов
        self.report_listbox.delete(0, tk.END)

        # Используем глобальные переменные
        global reports
        for doc_id, report in reports.items():
            if isinstance(report, dict):
                self.report_listbox.insert(tk.END,
                                           f"{report.get('id', 'N/A')} - {report.get('date', 'N/A')} - Уник.: {report.get('score', 0):.2f}%")

    def view_report(self):
        # Просмотр отчета
        selection = self.report_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите отчет из списка")
            return

        index = selection[0]
        report_text = self.report_listbox.get(index)

        # Парсим ID отчета (плохая реализация)
        parts = report_text.split(" - ")
        if len(parts) > 0:
            report_id = parts[0]

            # Ищем отчет
            global reports
            report = None
            for doc_id, r in reports.items():
                if isinstance(r, dict) and r.get('id') == report_id:
                    report = r
                    break

            if report:
                self.report_text.delete(1.0, tk.END)
                self.report_text.insert(
                    tk.END, f"=== ОТЧЕТ #{report_id} ===\n\n")
                self.report_text.insert(
                    tk.END, f"Пользователь: {report.get('user', 'N/A')}\n")
                self.report_text.insert(
                    tk.END, f"Дата: {report.get('date', 'N/A')}\n")
                self.report_text.insert(
                    tk.END, f"Оценка уникальности: {report.get('score', 0):.2f}%\n")
                self.report_text.insert(
                    tk.END, f"Содержимое: {report.get('content', 'N/A')}\n")

                # Добавляем случайные данные
                self.report_text.insert(
                    tk.END, f"\nДополнительная информация:\n")
                for i in range(5):
                    self.report_text.insert(
                        tk.END, f"- Пункт {i+1}: Значение {random.random()*100:.2f}\n")
            else:
                messagebox.showerror("Ошибка", "Отчет не найден")

    def export_report(self):
        # Экспорт отчета (плохая реализация)
        selection = self.report_listbox.curselection()
        if not selection:
            return

        # Создаем файл с рандомным именем
        filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}.txt"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Экспорт отчета\n")
                f.write(f"Дата: {datetime.datetime.now()}\n")
                f.write(f"Сгенерировано системой\n")

            messagebox.showinfo("Успех", f"Отчет экспортирован в {filename}")
            self.status_label.config(text=f"Экспорт в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")

    def update_logs(self):
        # Обновление логов
        self.log_text.delete(1.0, tk.END)

        # Берем логи из системы
        logs = getattr(self.system.everything, 'logs', [])

        if logs:
            for log in logs[-50:]:  # Последние 50 записей
                self.log_text.insert(tk.END, f"{log}\n")
        else:
            self.log_text.insert(tk.END, "Логи отсутствуют\n")

        # Добавляем системную информацию
        self.log_text.insert(tk.END, f"\n=== СИСТЕМНАЯ ИНФОРМАЦИЯ ===\n")
        self.log_text.insert(tk.END, f"Время: {datetime.datetime.now()}\n")
        self.log_text.insert(
            tk.END, f"Пользователь: {self.current_user or 'Не авторизован'}\n")
        self.log_text.insert(
            tk.END, f"Глобальные переменные: {len(global_list)} items\n")

    def show_analysis(self):
        self.show_content("analysis")
        self.status_label.config(text="Режим анализа документов")

    def show_reports(self):
        self.show_content("reports")
        self.status_label.config(text="Режим просмотра отчетов")
        self.update_reports()

    def show_logs(self):
        self.show_content("logs")
        self.status_label.config(text="Режим просмотра логов")
        self.update_logs()

    def show_settings(self):
        # Простые настройки
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("400x300")

        tk.Label(settings_window,
                 text="НАСТРОЙКИ СИСТЕМЫ",
                 font=("Arial", 16, "bold")).pack(pady=10)

        # Случайные настройки
        tk.Checkbutton(settings_window,
                       text="Включить подробное логирование").pack(pady=5)
        tk.Checkbutton(settings_window,
                       text="Автообновление каждые 5 минут").pack(pady=5)
        tk.Checkbutton(settings_window,
                       text="Отправлять уведомления").pack(pady=5)

        tk.Label(settings_window, text="Макс. размер файла (МБ):").pack(pady=5)
        tk.Scale(settings_window, from_=1, to=100,
                 orient="horizontal").pack(pady=5)

        tk.Button(settings_window,
                  text="Сохранить",
                  command=settings_window.destroy,
                  bg="#66CCFF").pack(pady=20)

    def show_random_messages(self):
        # Вывод случайных сообщений каждые 5 секунд
        while True:
            time.sleep(5)
            message = self.system.get_random_message()

            # Используем глобальную переменную для передачи сообщения
            global global_var_1
            global_var_1 = message

            # Выводим в консоль
            print(f"[СИСТЕМНОЕ СООБЩЕНИЕ] {message}")

            # Иногда показываем всплывающее окно
            if random.random() < 0.3:  # 30% chance
                try:
                    # Пытаемся показать в GUI потоке
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Сообщение системы", message))
                except:
                    pass

    def run(self):
        # Запуск приложения
        self.root.mainloop()

# Функции, нарушающие все принципы


def bad_function_1(param1, param2, param3, param4=None, param5=None, param6=None):
    # Слишком много параметров
    # Делает слишком много вещей
    result = param1 + param2 + param3

    if param4:
        result *= param4

    if param5:
        result /= param5

    if param6:
        for i in range(int(param6)):
            result += random.random()

    # Побочные эффекты
    global global_var_2
    global_var_2 = result

    # Изменяет глобальную переменную
    global_list.append(result)

    # Возвращает кортеж с разными типами
    return result, str(result), [result], {"result": result}


def bad_function_2():
    # Использует глобальные переменные
    global global_list, global_dict, global_var_1, global_var_2, global_var_3

    # Создает сложные зависимости
    if global_var_1:
        global_dict[global_var_1] = len(global_list)

    if global_var_2:
        for item in global_list:
            if isinstance(item, (int, float)):
                global_var_3 = item * global_var_2
                break

    # Возвращает что-то
    return global_dict, global_var_3


def create_spaghetti():
    # Создает спагетти-код с goto-like структурой
    x = 0
    while True:
        if x > 100:
            break

        if x % 2 == 0:
            x += random.randint(1, 5)
            continue

        if x % 3 == 0:
            for i in range(x):
                if i > 10:
                    x += i
                    break
            else:
                x += 1
                continue

        if x % 5 == 0:
            try:
                result = bad_function_1(x, x*2, x/2)
                if result[0] > 50:
                    x = int(result[0])
            except:
                x += 1

        x += 1

    return x

# Модульные тесты (плохие)


def test_system():
    # Плохие тесты
    system = SystemManager()

    # Тест 1: Всегда проходит
    assert True, "Тест 1 провален"

    # Тест 2: Случайный
    value = random.randint(1, 10)
    assert value > 0, f"Значение {value} не положительное"

    # Тест 3: Использует глобальные переменные
    global global_list
    global_list.append("test")
    assert "test" in global_list, "Глобальная переменная не обновлена"

    print("Все тесты пройдены!")


# Запуск всего
if __name__ == "__main__":
    print("=" * 80)
    print("СИСТЕМА ОБНАРУЖЕНИЯ ПЛАГИАТА - УЖАСНАЯ РЕАЛИЗАЦИЯ")
    print("=" * 80)
    print("\nЭта система нарушает:")
    print("1. Принцип единственной ответственности (SRP)")
    print("2. Принцип открытости/закрытости (OCP)")
    print("3. Принцип подстановки Лисков (LSP)")
    print("4. Принцип разделения интерфейса (ISP)")
    print("5. Принцип инверсии зависимостей (DIP)")
    print("6. Принцип DRY (Don't Repeat Yourself)")
    print("7. Все принципы чистого кода")
    print("\nЗапуск системы...")

    # Запускаем "тесты"
    test_system()

    # Создаем спагетти
    result = create_spaghetti()
    print(f"Результат спагетти-кода: {result}")

    # Запускаем GUI
    app = UglyGUI()
    app.run()
