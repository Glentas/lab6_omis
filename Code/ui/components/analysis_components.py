import streamlit as st
from typing import List, Dict, Any
import plotly.graph_objects as go
from datetime import datetime


class AnalysisComponents:
    """Компоненты для анализа плагиата"""
    
    @staticmethod
    def render_check_progress(check: Dict[str, Any]):
        """Рендер прогресса проверки"""
        st.markdown("""
        <h3 style='margin-bottom: 20px;'>🔍 Проверка на плагиат</h3>
        """, unsafe_allow_html=True)
        
        # Прогресс бар
        progress = check.get('progress', 0)
        status = check.get('status', 'processing')
        
        st.progress(progress / 100, text=f"Выполнение: {progress}%")
        
        # Статус проверки
        status_display = {
            'pending': '🟡 Ожидает начала',
            'processing': '🔵 В процессе',
            'completed': '✅ Завершено',
            'failed': '❌ Ошибка'
        }
        
        st.markdown(f"**Статус:** {status_display.get(status, status)}")
        
        # Информация о проверке
        check_date = check.get('check_date', '')
        if check_date:
            try:
                date_obj = datetime.fromisoformat(check_date.replace('Z', '+00:00'))
                check_date = date_obj.strftime("%d.%m.%Y %H:%M:%S")
            except:
                pass
        
        st.markdown(f"""
        **📅 Дата начала:** {check_date}
        
        **🎯 Цель проверки:** Анализ документа на наличие заимствований
        """)
        
        # Кнопки управления
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Обновить статус", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📊 Просмотреть результаты", use_container_width=True, disabled=status != 'completed'):
                st.session_state['view_results_check_id'] = check.get('check_id')
                st.rerun()
        
        with col3:
            if st.button("🔙 Назад", use_container_width=True):
                if 'check_doc_id' in st.session_state:
                    del st.session_state['check_doc_id']
                st.rerun()
    
    @staticmethod
    def render_check_results(results: Dict[str, Any]):
        """Рендер результатов проверки"""
        uniqueness = results.get('uniqueness_score', 0)
        matches = results.get('matches', [])
        
        st.markdown(f"""
        <h3 style='margin-bottom: 20px;'>📊 Результаты проверки</h3>
        """, unsafe_allow_html=True)
        
        # Основные метрики
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Индикатор уникальности
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=uniqueness,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Уникальность (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "red"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': uniqueness
                    }
                }
            ))
            fig_gauge.update_layout(height=250)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.metric("🔍 Найдено совпадений", len(matches))
        
        with col3:
            plagiarism_level = AnalysisComponents._get_plagiarism_level(uniqueness)
            st.metric("📈 Уровень плагиата", plagiarism_level)
        
        # Визуализация распределения совпадений
        if matches:
            st.markdown("### 📊 Распределение совпадений")
            
            # Группировка по уровню схожести
            high_matches = [m for m in matches if m.get('similarity', 0) > 0.9]
            medium_matches = [m for m in matches if 0.7 <= m.get('similarity', 0) <= 0.9]
            low_matches = [m for m in matches if m.get('similarity', 0) < 0.7]
            
            fig_dist = go.Figure(data=[
                go.Bar(
                    name='Высокая (>90%)',
                    x=['Совпадения'],
                    y=[len(high_matches)],
                    marker_color='red'
                ),
                go.Bar(
                    name='Средняя (70-90%)',
                    x=['Совпадения'],
                    y=[len(medium_matches)],
                    marker_color='orange'
                ),
                go.Bar(
                    name='Низкая (<70%)',
                    x=['Совпадения'],
                    y=[len(low_matches)],
                    marker_color='yellow'
                )
            ])
            
            fig_dist.update_layout(
                barmode='stack',
                title="Распределение по степени схожести",
                height=300
            )
            
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Детали совпадений
        if matches:
            st.markdown("### 📋 Детали совпадений")
            
            for i, match in enumerate(matches[:10]):  # Показываем первые 10 совпадений
                with st.expander(f"Совпадение #{i+1} - {match.get('match_percentage', 0):.1f}% схожести", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **📝 Фрагмент текста:**
                        ```
                        {match.get('fragment_context', 'Нет данных')}
                        ```
                        
                        **📍 Позиция:** {match.get('position_in_text', 'Неизвестно')}
                        """)
                    
                    with col2:
                        similarity = match.get('similarity', 0) * 100
                        
                        # Индикатор схожести
                        if similarity > 90:
                            color = "🔴 Высокая"
                        elif similarity > 70:
                            color = "🟡 Средняя"
                        else:
                            color = "🟢 Низкая"
                        
                        st.markdown(f"""
                        **📊 Схожесть:** {similarity:.1f}%
                        
                        **🎯 Уровень:** {color}
                        """)
        
        # Кнопки действий
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("📋 Создать отчет", type="primary", use_container_width=True):
                st.session_state['generate_report_check_id'] = results.get('check_id')
                st.rerun()
        
        with col2:
            if st.button("🔙 К списку проверок", use_container_width=True):
                if 'view_results_check_id' in st.session_state:
                    del st.session_state['view_results_check_id']
                st.rerun()
        
        with col3:
            if st.button("📁 Новый документ", use_container_width=True):
                st.session_state.clear()
                st.session_state['page'] = 'dashboard'
                st.rerun()
    
    @staticmethod
    def render_checks_list(checks: List[Dict[str, Any]]):
        """Рендер списка проверок"""
        if not checks:
            st.info("📭 У вас пока нет проверок")
            return
        
        st.markdown(f"""
        <h3 style='margin-bottom: 20px;'>📋 История проверок ({len(checks)})</h3>
        """, unsafe_allow_html=True)
        
        for check in checks:
            with st.expander(
                f"🔍 Проверка от {check.get('check_date', '')[:10]} - {check.get('document_name', 'Без названия')}",
                expanded=False
            ):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Информация о проверке
                    status = check.get('status', '')
                    status_icons = {
                        'pending': '🟡',
                        'processing': '🔵',
                        'completed': '✅',
                        'failed': '❌'
                    }
                    
                    st.markdown(f"""
                    **{status_icons.get(status, '❓')} Статус:** {status}
                    
                    **📅 Дата:** {check.get('check_date', '')}
                    
                    **📄 Документ:** {check.get('document_name', 'Неизвестно')}
                    """)
                    
                    if status == 'completed':
                        st.markdown(f"**🎯 Уникальность:** {check.get('unique_percentage', 0):.1f}%")
                
                with col2:
                    check_id = check.get('check_id')
                    if st.button("👁️ Просмотр", key=f"view_check_{check_id}", use_container_width=True):
                        st.session_state['view_results_check_id'] = check_id
                
                with col3:
                    if check.get('status') == 'completed':
                        if st.button("📊 Отчет", key=f"report_{check_id}", use_container_width=True):
                            st.session_state['generate_report_check_id'] = check_id
    
    @staticmethod
    def _get_plagiarism_level(uniqueness: float) -> str:
        """Определение уровня плагиата"""
        if uniqueness >= 90:
            return "Очень низкий"
        elif uniqueness >= 70:
            return "Низкий"
        elif uniqueness >= 50:
            return "Средний"
        elif uniqueness >= 30:
            return "Высокий"
        else:
            return "Критический"
