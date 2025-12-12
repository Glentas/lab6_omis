import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import streamlit as st

from app.core.models import Report
from app.storage.json_storage import StorageManager
from app.core.config import AppConfig


class ReportGenerator:
    """Генератор отчетов"""
    
    def __init__(self, storage: StorageManager):
        self.storage = storage
    
    def generate_report(self, check_id: str, user_id: str) -> Dict[str, Any]:
        """Генерация отчета по проверке"""
        try:
            # Получение результатов проверки
            check = self.storage.checks.read("checks", check_id)
            if not check:
                return {"success": False, "message": "Проверка не найдена"}
            
            results = self.storage.results.find("results", check_id=check_id)
            if not results:
                return {"success": False, "message": "Результаты проверки не найдены"}
            
            result = results[0]
            doc_id = check.get("doc_id")
            document = self.storage.documents.read("documents", doc_id) if doc_id else None
            
            # Создание отчета
            report_id = str(uuid.uuid4())
            report_data = {
                "report_id": report_id,
                "check_id": check_id,
                "user_id": user_id,
                "generated_date": datetime.now().isoformat(),
                "unique_percentage": result.get("uniqueness_score", 0),
                "match_count": len(result.get("matches", [])),
                "summary": self._generate_summary(check, result, document)
            }
            
            self.storage.reports.create("reports", report_data, report_id)
            
            return {
                "success": True,
                "report_id": report_id,
                "report_data": report_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка при генерации отчета: {str(e)}"
            }
    
    def _generate_summary(self, check: Dict[str, Any], 
                          result: Dict[str, Any], 
                          document: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Генерация сводки отчета"""
        uniqueness = result.get("uniqueness_score", 0)
        matches = result.get("matches", [])
        
        # Анализ совпадений по уровню схожести
        high_matches = [m for m in matches if m.get("similarity", 0) > 0.9]
        medium_matches = [m for m in matches if 0.7 <= m.get("similarity", 0) <= 0.9]
        low_matches = [m for m in matches if m.get("similarity", 0) < 0.7]
        
        summary = {
            "document_name": document.get("file_name", "Неизвестный документ") if document else "Неизвестный документ",
            "check_date": check.get("check_date", ""),
            "uniqueness_score": uniqueness,
            "plagiarism_level": self._get_plagiarism_level(uniqueness),
            "total_matches": len(matches),
            "high_similarity_matches": len(high_matches),
            "medium_similarity_matches": len(medium_matches),
            "low_similarity_matches": len(low_matches),
            "top_sources": self._get_top_sources(result),
            "match_distribution": {
                "high": len(high_matches),
                "medium": len(medium_matches),
                "low": len(low_matches)
            }
        }
        
        return summary
    
    def _get_plagiarism_level(self, uniqueness: float) -> str:
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
    
    def _get_top_sources(self, result: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Получение топ источников совпадений"""
        matches = result.get("matches", [])
        sources = result.get("sources", [])
        
        # Подсчет совпадений по источникам
        source_counts = {}
        for match in matches:
            source_id = match.get("source_id")
            if source_id:
                source_counts[source_id] = source_counts.get(source_id, 0) + 1
        
        # Сортировка по количеству совпадений
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        
        top_sources = []
        for source_id, count in sorted_sources[:limit]:
            source_info = next((s for s in sources if s.get("source_id") == source_id), {})
            top_sources.append({
                "source_id": source_id,
                "source_name": source_info.get("source_name", "Неизвестный источник"),
                "author": source_info.get("author", "Неизвестный автор"),
                "match_count": count
            })
        
        return top_sources
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Получение отчета"""
        report = self.storage.reports.read("reports", report_id)
        if not report:
            return None
        
        # Добавление детальной информации
        check_id = report.get("check_id")
        if check_id:
            check = self.storage.checks.read("checks", check_id)
            if check:
                report["check_details"] = check
                
                # Получение результатов
                results = self.storage.results.find("results", check_id=check_id)
                if results:
                    report["analysis_results"] = results[0]
        
        return report
    
    def get_user_reports(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение отчетов пользователя"""
        reports = self.storage.reports.find("reports", user_id=user_id)
        
        # Добавление информации о проверках
        for report in reports:
            check_id = report.get("check_id")
            if check_id:
                check = self.storage.checks.read("checks", check_id)
                if check:
                    report["check_status"] = check.get("status")
                    
                    doc_id = check.get("doc_id")
                    if doc_id:
                        document = self.storage.documents.read("documents", doc_id)
                        if document:
                            report["document_name"] = document.get("file_name")
        
        return sorted(reports, key=lambda x: x.get("generated_date", ""), reverse=True)
    
    def create_visualizations(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Создание визуализаций для отчета"""
        visualizations = {}
        
        # 1. Круговая диаграмма уникальности
        uniqueness = report.get("unique_percentage", 0)
        plagiarism = 100 - uniqueness
        
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=['Уникальность', 'Заимствования'],
                values=[uniqueness, plagiarism],
                hole=.3,
                marker_colors=['#28a745', '#dc3545']
            )
        ])
        fig_pie.update_layout(title="Соотношение уникальности и заимствований")
        visualizations["uniqueness_pie"] = fig_pie
        
        # 2. Распределение совпадений по степени схожести
        summary = report.get("summary", {})
        match_dist = summary.get("match_distribution", {})
        
        if match_dist:
            fig_bar = px.bar(
                x=["Высокая", "Средняя", "Низкая"],
                y=[match_dist.get("high", 0), match_dist.get("medium", 0), match_dist.get("low", 0)],
                title="Распределение совпадений по степени схожести",
                labels={"x": "Степень схожести", "y": "Количество совпадений"},
                color=["Высокая", "Средняя", "Низкая"],
                color_discrete_map={"Высокая": "#dc3545", "Средняя": "#ffc107", "Низкая": "#17a2b8"}
            )
            visualizations["match_distribution"] = fig_bar
        
        # 3. Топ источников
        top_sources = summary.get("top_sources", [])
        if top_sources:
            source_names = [s.get("source_name", f"Источник {i+1}") for i, s in enumerate(top_sources)]
            source_counts = [s.get("match_count", 0) for s in top_sources]
            
            fig_sources = px.bar(
                x=source_counts,
                y=source_names,
                orientation='h',
                title="Топ источников заимствований",
                labels={"x": "Количество совпадений", "y": "Источник"},
                color=source_counts,
                color_continuous_scale='Reds'
            )
            visualizations["top_sources"] = fig_sources
        
        return visualizations
    
    def export_report_to_json(self, report_id: str) -> Optional[Path]:
        """Экспорт отчета в JSON"""
        report = self.get_report(report_id)
        if not report:
            return None
        
        # Создание директории для экспорта
        export_dir = AppConfig.REPORTS_DIR / "json"
        export_dir.mkdir(exist_ok=True)
        
        # Сохранение в файл
        filename = f"report_{report_id}.json"
        filepath = export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
    
    def get_report_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Получение статистики по отчетам"""
        if user_id:
            reports = self.storage.reports.find("reports", user_id=user_id)
        else:
            reports = self.storage.reports.read_all("reports")
        
        if not reports:
            return {}
        
        # Расчет статистики
        uniqueness_scores = [r.get("unique_percentage", 0) for r in reports]
        match_counts = [r.get("match_count", 0) for r in reports]
        
        stats = {
            "total_reports": len(reports),
            "avg_uniqueness": sum(uniqueness_scores) / len(uniqueness_scores) if uniqueness_scores else 0,
            "avg_matches": sum(match_counts) / len(match_counts) if match_counts else 0,
            "min_uniqueness": min(uniqueness_scores) if uniqueness_scores else 0,
            "max_uniqueness": max(uniqueness_scores) if uniqueness_scores else 0,
            "recent_reports": reports[:5]  # Последние 5 отчетов
        }
        
        return stats
