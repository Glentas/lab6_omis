import streamlit as st
from typing import Dict, Any
import json
from pathlib import Path
import tempfile


class ReportComponents:
    """Компоненты для работы с отчетами"""
    
    @staticmethod
    def render_report_details(report: Dict[str, Any], visualizations: Dict[str, Any]):
        """Рендер деталей отчета"""
        st.markdown(f"""
        <h3 style='margin-bottom: 20px;'>📊 Отчет о проверке плагиата</h3>
        """, unsafe_allow_html=True)
        
        # Основная информация
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎯 Уникальность", 
                f"{report.get('unique_percentage', 0):.1f}%",
                delta=f"{report.get('unique_percentage', 0) - 50:.1f}% от среднего"
            )
        
        with col2:
            st.metric(
                "🔍 Совпадений", 
                report.get('match_count', 0)
            )
        
        with col3:
            generated_date = report.get('generated_date', '')
            if generated_date:
                from datetime import datetime
                try:
                    date_obj = datetime.fromisoformat(generated_date.replace('Z', '+00:00'))
                    generated_date = date_obj.strftime("%d.%m.%Y")
                except:
                    pass
            
            st.metric("📅 Дата отчета", generated_date)
        
        with col4:
            report_id = report.get('report_id', '')[:8]
            st.metric("📋 ID отчета", f"#{report_id}")
        
        # Визуализации
        if visualizations:
            st.markdown("### 📈 Визуализации")
            
            # Круговая диаграмма уникальности
            if "uniqueness_pie" in visualizations:
                st.plotly_chart(visualizations["uniqueness_pie"], use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if "match_distribution" in visualizations:
                    st.plotly_chart(visualizations["match_distribution"], use_container_width=True)
            
            with col2:
                if "top_sources" in visualizations:
                    st.plotly_chart(visualizations["top_sources"], use_container_width=True)
        
        # Сводка отчета
        summary = report.get('summary', {})
        if summary:
            st.markdown("### 📋 Сводка отчета")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                **📄 Документ:** {summary.get('document_name', 'Неизвестно')}
                
                **📊 Уровень плагиата:** {summary.get('plagiarism_level', 'Неизвестно')}
                
                **🔍 Всего совпадений:** {summary.get('total_matches', 0)}
                """)
            
            with col2:
                match_dist = summary.get('match_distribution', {})
                st.markdown(f"""
                **🎯 Распределение совпадений:**
                - Высокая схожесть: {match_dist.get('high', 0)}
                - Средняя схожесть: {match_dist.get('medium', 0)}
                - Низкая схожесть: {match_dist.get('low', 0)}
                """)
        
        # Топ источников
        top_sources = summary.get('top_sources', []) if summary else []
        if top_sources:
            st.markdown("### 📚 Топ источников заимствований")
            
            for i, source in enumerate(top_sources[:5]):
                with st.expander(f"{i+1}. {source.get('source_name', 'Неизвестный источник')}", expanded=False):
                    st.markdown(f"""
                    **✍️ Автор:** {source.get('author', 'Неизвестен')}
                    
                    **🔗 Количество совпадений:** {source.get('match_count', 0)}
                    
                    **📊 Влияние на уникальность:** {(source.get('match_count', 0) / max(summary.get('total_matches', 1), 1) * 100):.1f}%
                    """)
        
        # Кнопки экспорта
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("📥 Экспорт в JSON", use_container_width=True):
                st.session_state['export_report_id'] = report.get('report_id')
                st.session_state['export_format'] = 'json'
                st.rerun()
        
        with col2:
            if st.button("📋 Новый отчет", use_container_width=True):
                if 'selected_report_id' in st.session_state:
                    del st.session_state['selected_report_id']
                st.rerun()
        
        with col3:
            if st.button("🔙 К списку отчетов", use_container_width=True):
                if 'selected_report_id' in st.session_state:
                    del st.session_state['selected_report_id']
                st.rerun()
    
    @staticmethod
    def render_reports_list(reports: List[Dict[str, Any]]):
        """Рендер списка отчетов"""
        if not reports:
            st.info("📭 У вас пока нет отчетов")
            return
        
        st.markdown(f"""
        <h3 style='margin-bottom: 20px;'>📁 Ваши отчеты ({len(reports)})</h3>
        """, unsafe_allow_html=True)
        
        for report in reports:
            with st.expander(
                f"📊 Отчет от {report.get('generated_date', '')[:10]} - {report.get('document_name', 'Без названия')}",
                expanded=False
            ):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Информация об отчете
                    uniqueness = report.get('unique_percentage', 0)
                    match_count = report.get('match_count', 0)
                    
                    # Определение цвета для уникальности
                    if uniqueness >= 80:
                        color = "🟢"
                    elif uniqueness >= 60:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.markdown(f"""
                    **{color} Уникальность:** {uniqueness:.1f}%
                    
                    **🔍 Совпадений:** {match_count}
                    
                    **📄 Документ:** {report.get('document_name', 'Неизвестно')}
                    
                    **📅 Дата создания:** {report.get('generated_date', '')[:10]}
                    """)
                
                with col2:
                    report_id = report.get('report_id')
                    if st.button("👁️ Просмотр", key=f"view_report_{report_id}", use_container_width=True):
                        st.session_state['selected_report_id'] = report_id
                
                with col3:
                    if st.button("📥 Экспорт", key=f"export_{report_id}", use_container_width=True):
                        st.session_state['export_report_id'] = report_id
    
    @staticmethod
    def create_json_export(report: Dict[str, Any]) -> str:
        """Создание JSON экспорта"""
        export_data = {
            "report_id": report.get("report_id"),
            "generated_date": report.get("generated_date"),
            "unique_percentage": report.get("unique_percentage"),
            "match_count": report.get("match_count"),
            "summary": report.get("summary", {}),
            "check_details": report.get("check_details", {}),
            "analysis_results": report.get("analysis_results", {})
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    @staticmethod
    def render_export_dialog(report: Dict[str, Any], export_format: str):
        """Рендер диалога экспорта"""
        st.success("✅ Отчет готов к экспорту!")
        
        if export_format == 'json':
            json_data = ReportComponents.create_json_export(report)
            
            # Создание временного файла
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(json_data)
                temp_path = f.name
            
            # Кнопка скачивания
            with open(temp_path, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="⬇️ Скачать JSON файл",
                    data=f.read(),
                    file_name=f"plagiarism_report_{report.get('report_id', '')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Очистка временного файла
            Path(temp_path).unlink(missing_ok=True)
        
        # Кнопка возврата
        if st.button("🔙 Вернуться к отчету", use_container_width=True):
            if 'export_report_id' in st.session_state:
                del st.session_state['export_report_id']
            if 'export_format' in st.session_state:
                del st.session_state['export_format']
            st.rerun()

