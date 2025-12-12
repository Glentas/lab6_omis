import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import plotly.express as px


class AdminComponents:
    """Компоненты для административной панели"""
    
    @staticmethod
    def render_admin_dashboard(stats: Dict[str, Any]):
        """Рендер административной панели"""
        st.markdown("""
        <h1 style='text-align: center;'>👨‍💼 Административная панель</h1>
        <p style='text-align: center; color: #666;'>Управление системой проверки плагиата</p>
        """, unsafe_allow_html=True)
        
        # Статистика системы
        st.markdown("### 📊 Статистика системы")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Пользователей", stats.get('total_users', 0))
        
        with col2:
            st.metric("📄 Документов", stats.get('total_documents', 0))
        
        with col3:
            st.metric("🔍 Проверок", stats.get('total_checks', 0))
        
        with col4:
            st.metric("📊 Отчетов", stats.get('total_reports', 0))
        
        # Быстрые действия
        st.markdown("### 🚀 Быстрые действия")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👥 Управление пользователями", use_container_width=True, icon="👥"):
                st.session_state['admin_page'] = 'user_management'
                st.rerun()
        
        with col2:
            if st.button("📊 Мониторинг", use_container_width=True, icon="📊"):
                st.session_state['admin_page'] = 'monitoring'
                st.rerun()
        
        with col3:
            if st.button("⚙️ Настройки", use_container_width=True, icon="⚙️"):
                st.session_state['admin_page'] = 'settings'
                st.rerun()
        
        with col4:
            if st.button("📋 Журнал аудита", use_container_width=True, icon="📋"):
                st.session_state['admin_page'] = 'audit_log'
                st.rerun()
        
        # Недавняя активность
        recent_checks = stats.get('recent_checks', [])
        if recent_checks:
            st.markdown("### ⏱️ Недавняя активность")
            
            df = pd.DataFrame(recent_checks)
            if not df.empty:
                # Преобразование дат
                if 'check_date' in df.columns:
                    df['check_date'] = pd.to_datetime(df['check_date']).dt.strftime("%Y-%m-%d %H:%M")
                
                # Отображение таблицы
                st.dataframe(
                    df[['check_date', 'document_name', 'user_name', 'unique_percentage', 'status']].head(10),
                    use_container_width=True,
                    column_config={
                        'check_date': 'Дата',
                        'document_name': 'Документ',
                        'user_name': 'Пользователь',
                        'unique_percentage': 'Уникальность',
                        'status': 'Статус'
                    }
                )
    
    @staticmethod
    def render_user_management(users: List[Dict[str, Any]]):
        """Рендер управления пользователями"""
        st.markdown("### 👥 Управление пользователями")
        
        # Кнопка добавления пользователя
        if st.button("➕ Добавить пользователя", icon="➕"):
            st.session_state['admin_action'] = 'add_user'
            st.rerun()
        
        # Таблица пользователей
        if users:
            df = pd.DataFrame(users)
            
            # Преобразование дат
            if 'registration_date' in df.columns:
                df['registration_date'] = pd.to_datetime(df['registration_date']).dt.strftime("%Y-%m-%d")
            
            # Отображение таблицы
            edited_df = st.data_editor(
                df[['user_id', 'name', 'email', 'role', 'registration_date']],
                use_container_width=True,
                column_config={
                    'user_id': st.column_config.TextColumn("ID", disabled=True),
                    'name': st.column_config.TextColumn("Имя"),
                    'email': st.column_config.TextColumn("Email"),
                    'role': st.column_config.SelectboxColumn(
                        "Роль",
                        options=["student", "teacher", "admin"]
                    ),
                    'registration_date': st.column_config.TextColumn("Дата регистрации", disabled=True),
                    'actions': st.column_config.TextColumn("Действия", disabled=True)
                },
                num_rows="dynamic"
            )
            
            # Кнопки действий
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Сохранить изменения", use_container_width=True, type="primary"):
                    st.success("Изменения сохранены!")
            
            with col2:
                if st.button("🔙 Назад", use_container_width=True):
                    st.session_state['admin_page'] = 'dashboard'
                    st.rerun()
    
    @staticmethod
    def render_monitoring(stats: Dict[str, Any]):
        """Рендер мониторинга системы"""
        st.markdown("### 📊 Мониторинг системы")
        
        # Общая статистика
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Активных сессий", stats.get('active_sessions', 0))
        
        with col2:
            st.metric("Загружено сегодня", stats.get('uploads_today', 0))
        
        with col3:
            st.metric("Проверок сегодня", stats.get('checks_today', 0))
        
        # График активности
        activity_data = stats.get('activity_data', {})
        if activity_data:
            dates = list(activity_data.keys())
            uploads = [activity_data[date].get('uploads', 0) for date in dates]
            checks = [activity_data[date].get('checks', 0) for date in dates]
            
            fig = px.line(
                x=dates,
                y=[uploads, checks],
                labels={'x': 'Дата', 'y': 'Количество', 'variable': 'Тип'},
                title="Активность системы за последние 7 дней",
                markers=True
            )
            
            fig.data[0].name = "Загрузки"
            fig.data[1].name = "Проверки"
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Распределение по ролям
        role_distribution = stats.get('role_distribution', {})
        if role_distribution:
            roles = list(role_distribution.keys())
            counts = list(role_distribution.values())
            
            fig_pie = px.pie(
                values=counts,
                names=roles,
                title="Распределение пользователей по ролям"
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Кнопка возврата
        if st.button("🔙 Назад", use_container_width=True):
            st.session_state['admin_page'] = 'dashboard'
            st.rerun()
    
    @staticmethod
    def render_settings():
        """Рендер настроек системы"""
        st.markdown("### ⚙️ Настройки системы")
        
        # Настройки безопасности
        with st.expander("🔒 Настройки безопасности", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                session_timeout = st.number_input(
                    "Таймаут сессии (минуты)",
                    min_value=5,
                    max_value=480,
                    value=30,
                    help="Время неактивности до автоматического выхода"
                )
            
            with col2:
                max_file_size = st.number_input(
                    "Макс. размер файла (MB)",
                    min_value=1,
                    max_value=100,
                    value=50,
                    help="Максимальный размер загружаемого файла"
                )
        
        # Настройки анализа
        with st.expander("🔍 Настройки анализа", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                similarity_threshold = st.slider(
                    "Порог схожести (%)",
                    min_value=50,
                    max_value=100,
                    value=80,
                    help="Минимальная схожесть для обнаружения плагиата"
                )
            
            with col2:
                min_match_length = st.number_input(
                    "Мин. длина совпадения",
                    min_value=5,
                    max_value=100,
                    value=20,
                    help="Минимальная длина текста для обнаружения совпадения"
                )
        
        # Кнопки сохранения
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("💾 Сохранить настройки", use_container_width=True, type="primary"):
                st.success("Настройки сохранены!")
        
        with col2:
            if st.button("🔙 Назад", use_container_width=True):
                st.session_state['admin_page'] = 'dashboard'
                st.rerun()
    
    @staticmethod
    def render_audit_log(audit_logs: List[Dict[str, Any]]):
        """Рендер журнала аудита"""
        st.markdown("### 📋 Журнал аудита")
        
        # Фильтры
        col1, col2, col3 = st.columns(3)
        
        with col1:
            start_date = st.date_input("Дата начала")
        
        with col2:
            end_date = st.date_input("Дата окончания")
        
        with col3:
            event_type = st.selectbox(
                "Тип события",
                ["Все", "Вход", "Выход", "Загрузка", "Проверка", "Отчет"]
            )
        
        # Таблица логов
        if audit_logs:
            df = pd.DataFrame(audit_logs)
            
            # Применение фильтров
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                if start_date:
                    df = df[df['timestamp'].dt.date >= start_date]
                if end_date:
                    df = df[df['timestamp'].dt.date <= end_date]
                
                df['timestamp'] = df['timestamp'].dt.strftime("%Y-%m-%d %H:%M:%S")
            
            if event_type != "Все":
                df = df[df['event_type'] == event_type.lower()]
            
            # Отображение таблицы
            st.dataframe(
                df[['timestamp', 'user_name', 'event_type', 'event_details']],
                use_container_width=True,
                column_config={
                    'timestamp': 'Время',
                    'user_name': 'Пользователь',
                    'event_type': 'Тип события',
                    'event_details': 'Детали'
                }
            )
        
        # Кнопки
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 Обновить", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🔙 Назад", use_container_width=True):
                st.session_state['admin_page'] = 'dashboard'
                st.rerun()
