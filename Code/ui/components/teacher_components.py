import streamlit as st
from typing import List, Dict, Any
import pandas as pd


class TeacherComponents:
    """Компоненты для роли преподавателя"""
    
    @staticmethod
    def render_teacher_dashboard(stats: Dict[str, Any]):
        """Рендер панели преподавателя"""
        st.markdown("""
        <h1 style='text-align: center;'>👨‍🏫 Панель преподавателя</h1>
        <p style='text-align: center; color: #666;'>Управление студентами и проверками</p>
        """, unsafe_allow_html=True)
        
        # Статистика преподавателя
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Студентов", stats.get('total_students', 0))
        
        with col2:
            st.metric("📄 Проверенных работ", stats.get('checked_documents', 0))
        
        with col3:
            avg_uniqueness = stats.get('avg_uniqueness', 0)
            st.metric("📊 Средняя уникальность", f"{avg_uniqueness:.1f}%")
        
        # Быстрые действия
        st.markdown("### 🚀 Быстрые действия")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👥 Управление студентами", use_container_width=True, icon="👥"):
                st.session_state['teacher_page'] = 'manage_students'
                st.rerun()
        
        with col2:
            if st.button("📊 Статистика группы", use_container_width=True, icon="📊"):
                st.session_state['teacher_page'] = 'group_statistics'
                st.rerun()
        
        with col3:
            if st.button("📁 Все отчеты", use_container_width=True, icon="📁"):
                st.session_state['teacher_page'] = 'all_reports'
                st.rerun()
        
        # Недавние проверки студентов
        recent_checks = stats.get('recent_student_checks', [])
        if recent_checks:
            st.markdown("### 📋 Недавние проверки студентов")
            
            df = pd.DataFrame(recent_checks)
            if not df.empty:
                st.dataframe(
                    df[['student_name', 'document_name', 'check_date', 'unique_percentage']],
                    use_container_width=True,
                    column_config={
                        'student_name': 'Студент',
                        'document_name': 'Документ',
                        'check_date': 'Дата проверки',
                        'unique_percentage': 'Уникальность'
                    }
                )
    
    @staticmethod
    def render_manage_students(students: List[Dict[str, Any]]):
        """Рендер управления студентами"""
        st.markdown("### 👥 Управление студентами")
        
        # Поиск студентов
        search_query = st.text_input("🔍 Поиск студента по имени или email")
        
        # Таблица студентов
        if students:
            # Фильтрация по поисковому запросу
            if search_query:
                filtered_students = [
                    s for s in students 
                    if search_query.lower() in s.get('name', '').lower() 
                    or search_query.lower() in s.get('email', '').lower()
                ]
            else:
                filtered_students = students
            
            if filtered_students:
                for student in filtered_students:
                    with st.expander(f"👨‍🎓 {student.get('name', 'Без имени')}", expanded=False):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            # Информация о студенте
                            st.markdown(f"""
                            **📧 Email:** {student.get('email', 'Нет email')}
                            
                            **📅 Дата регистрации:** {student.get('registration_date', '')[:10]}
                            
                            **📊 Всего проверок:** {student.get('total_checks', 0)}
                            
                            **🎯 Средняя уникальность:** {student.get('avg_uniqueness', 0):.1f}%
                            """)
                        
                        with col2:
                            student_id = student.get('user_id')
                            if st.button("📁 Работы", key=f"works_{student_id}", use_container_width=True):
                                st.session_state['selected_student_id'] = student_id
                                st.session_state['teacher_page'] = 'student_works'
                                st.rerun()
                        
                        with col3:
                            if st.button("📊 Статистика", key=f"stats_{student_id}", use_container_width=True):
                                st.session_state['selected_student_id'] = student_id
                                st.session_state['teacher_page'] = 'student_statistics'
                                st.rerun()
            else:
                st.info("🚫 Студенты не найдены")
        
        # Кнопка возврата
        if st.button("🔙 Назад", use_container_width=True):
            st.session_state['teacher_page'] = 'dashboard'
            st.rerun()
    
    @staticmethod
    def render_group_statistics(stats: Dict[str, Any]):
        """Рендер статистики группы"""
        st.markdown("### 📊 Статистика группы")
        
        # Основные метрики группы
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Всего студентов", stats.get('total_students', 0))
        
        with col2:
            st.metric("Активных", stats.get('active_students', 0))
        
        with col3:
            st.metric("Всего работ", stats.get('total_works', 0))
        
        with col4:
            st.metric("Средняя уникальность", f"{stats.get('avg_group_uniqueness', 0):.1f}%")
        
        # Распределение по уровню уникальности
        uniqueness_dist = stats.get('uniqueness_distribution', {})
        if uniqueness_dist:
            st.markdown("#### 📈 Распределение по уровню уникальности")
            
            categories = ["<50%", "50-70%", "70-90%", ">90%"]
            values = [
                uniqueness_dist.get('low', 0),
                uniqueness_dist.get('medium', 0),
                uniqueness_dist.get('high', 0),
                uniqueness_dist.get('excellent', 0)
            ]
            
            # Создание DataFrame для визуализации
            import plotly.express as px
            import pandas as pd
            
            df = pd.DataFrame({
                'Категория': categories,
                'Количество': values
            })
            
            fig = px.bar(
                df, 
                x='Категория', 
                y='Количество',
                title='Распределение работ по уровню уникальности',
                color='Количество',
                color_continuous_scale='Viridis'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Топ студентов
        top_students = stats.get('top_students', [])
        if top_students:
            st.markdown("#### 🏆 Топ студентов по уникальности")
            
            for i, student in enumerate(top_students[:5]):
                col1, col2, col3 = st.columns([1, 3, 2])
                
                with col1:
                    st.markdown(f"**#{i+1}**")
                
                with col2:
                    st.markdown(f"**{student.get('name', 'Без имени')}**")
                
                with col3:
                    uniqueness = student.get('avg_uniqueness', 0)
                    st.markdown(f"**{uniqueness:.1f}%**")
        
        # Кнопка возврата
        if st.button("🔙 Назад", use_container_width=True):
            st.session_state['teacher_page'] = 'dashboard'
            st.rerun()
    
    @staticmethod
    def render_student_works(student_id: str, student_info: Dict[str, Any], works: List[Dict[str, Any]]):
        """Рендер работ студента"""
        st.markdown(f"### 📁 Работы студента: {student_info.get('name', 'Без имени')}")
        
        if works:
            for work in works:
                with st.expander(f"📄 {work.get('document_name', 'Без названия')}", expanded=False):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Информация о работе
                        st.markdown(f"""
                        **📅 Дата загрузки:** {work.get('upload_date', '')[:10]}
                        
                        **📊 Формат:** {work.get('format', 'Неизвестно')}
                        
                        **🎯 Уникальность:** {work.get('unique_percentage', 0):.1f}%
                        
                        **🔍 Совпадений:** {work.get('match_count', 0)}
                        """)
                    
                    with col2:
                        check_id = work.get('check_id')
                        if st.button("📊 Отчет", key=f"report_{check_id}", use_container_width=True):
                            st.session_state['selected_report_id'] = work.get('report_id')
                            st.rerun()
                    
                    with col3:
                        if st.button("👁️ Просмотр", key=f"view_{check_id}", use_container_width=True):
                            st.session_state['view_results_check_id'] = check_id
                            st.rerun()
        else:
            st.info("📭 У студента пока нет работ")
        
        # Кнопка возврата
        if st.button("🔙 Назад", use_container_width=True):
            if 'selected_student_id' in st.session_state:
                del st.session_state['selected_student_id']
            st.session_state['teacher_page'] = 'manage_students'
            st.rerun()
