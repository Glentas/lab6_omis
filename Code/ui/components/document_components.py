import streamlit as st
from typing import List, Dict, Any
from datetime import datetime
from app.core.config import AppConfig


class DocumentComponents:
    """Компоненты для работы с документами"""
    
    @staticmethod
    def render_upload_form():
        """Рендер формы загрузки документа"""
        st.markdown("""
        <h3 style='margin-bottom: 20px;'>📄 Загрузите документ для проверки</h3>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Выберите файл",
            type=[ext[1:] for ext in AppConfig.SUPPORTED_FORMATS],
            help=f"Поддерживаемые форматы: {', '.join(AppConfig.SUPPORTED_FORMATS)}"
        )
        
        if uploaded_file:
            file_size = uploaded_file.size / (1024 * 1024)  # Размер в MB
            
            if file_size > AppConfig.MAX_FILE_SIZE / (1024 * 1024):
                st.error(f"❌ Размер файла превышает {AppConfig.MAX_FILE_SIZE / (1024 * 1024)} MB")
                return None
            
            st.success(f"""
            ✅ Файл готов к загрузке:
            - **Название:** {uploaded_file.name}
            - **Размер:** {file_size:.2f} MB
            - **Тип:** {uploaded_file.type}
            """)
            
            return uploaded_file
        
        return None
    
    @staticmethod
    def render_document_list(documents: List[Dict[str, Any]]):
        """Рендер списка документов"""
        if not documents:
            st.info("📭 У вас пока нет загруженных документов")
            return
        
        st.markdown(f"""
        <h3 style='margin-bottom: 20px;'>📚 Ваши документы ({len(documents)})</h3>
        """, unsafe_allow_html=True)
        
        for doc in documents:
            with st.expander(f"📄 {doc.get('file_name', 'Без названия')}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Информация о документе
                    upload_date = doc.get('upload_date', '')
                    if upload_date:
                        try:
                            date_obj = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                            upload_date = date_obj.strftime("%d.%m.%Y %H:%M")
                        except:
                            pass
                    
                    st.markdown(f"""
                    **📋 Информация:**
                    - Формат: `{doc.get('format', 'Неизвестно')}`
                    - Размер: `{doc.get('file_size', 0) / 1024:.1f} KB`
                    - Дата загрузки: `{upload_date}`
                    """)
                    
                    # Статус обработки
                    status = doc.get('status', 'pending')
                    status_colors = {
                        'pending': '🟡 Ожидает обработки',
                        'in_progress': '🔵 В обработке',
                        'completed': '✅ Обработан',
                        'error': '❌ Ошибка'
                    }
                    st.markdown(f"**📊 Статус:** {status_colors.get(status, status)}")
                
                with col2:
                    # Кнопки действий
                    doc_id = doc.get('doc_id')
                    if st.button("👁️ Просмотр", key=f"view_{doc_id}", use_container_width=True):
                        st.session_state['selected_doc_id'] = doc_id
                    
                    if st.button("🗑️ Удалить", key=f"delete_{doc_id}", use_container_width=True):
                        st.session_state['delete_doc_id'] = doc_id
    
    @staticmethod
    def render_document_details(doc_id: str, document: Dict[str, Any]):
        """Рендер детальной информации о документе"""
        st.markdown(f"""
        <h3 style='margin-bottom: 20px;'>📋 Детали документа</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Основная информация
            st.markdown(f"""
            **📄 Название:** {document.get('file_name', 'Без названия')}
            
            **📊 Формат:** `{document.get('format', 'Неизвестно')}`
            
            **💾 Размер:** `{document.get('file_size', 0) / 1024:.1f} KB`
            
            **📅 Дата загрузки:** `{document.get('upload_date', 'Неизвестно')}`
            """)
        
        with col2:
            # Действия с документом
            if st.button("🔙 Назад к списку", use_container_width=True):
                del st.session_state['selected_doc_id']
                st.rerun()
            
            # Проверка на плагиат
            if document.get('processed'):
                if st.button("🔍 Проверить на плагиат", type="primary", use_container_width=True):
                    st.session_state['check_doc_id'] = doc_id
                    st.rerun()
            else:
                st.warning("Документ не обработан")
            
            # Просмотр текста
            if st.button("📝 Просмотреть текст", use_container_width=True):
                st.session_state['view_text_doc_id'] = doc_id
    
    @staticmethod
    def render_processed_text(text_data: Dict[str, Any]):
        """Рендер обработанного текста"""
        st.markdown("""
        <h3 style='margin-bottom: 20px;'>📝 Извлеченный текст</h3>
        """, unsafe_allow_html=True)
        
        # Статистика текста
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Символов", text_data.get('text_length', 0))
        with col2:
            st.metric("Слов", text_data.get('word_count', 0))
        with col3:
            sentences = text_data.get('extracted_text', '').count('.') + text_data.get('extracted_text', '').count('!') + text_data.get('extracted_text', '').count('?')
            st.metric("Предложений", sentences)
        with col4:
            st.metric("Статус", "✅ Готов")
        
        # Превью текста
        st.markdown("### 📋 Превью текста")
        extracted_text = text_data.get('extracted_text', '')
        preview_length = min(1000, len(extracted_text))
        
        with st.expander("Показать текст", expanded=True):
            st.text_area(
                "Текст документа",
                extracted_text[:preview_length] + ("..." if len(extracted_text) > preview_length else ""),
                height=300,
                disabled=True
            )
