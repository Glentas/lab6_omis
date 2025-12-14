import os
import re
import warnings
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import numpy as np
from app.core.text_preprocessor import TextPreprocessor

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    warnings.warn("PyPDF2 не установлен. PDF файлы не будут поддерживаться.")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    warnings.warn(
        "python-docx не установлен. DOCX файлы не будут поддерживаться.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn(
        "scikit-learn не установлен. Проверка будет использовать простой алгоритм.")


class FileLoader:
    """
    Класс для загрузки текста из файлов разных форматов.
    """

    @staticmethod
    def load_text_from_file(file_path: str) -> str:

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        try:
            if suffix == '.txt':
                return FileLoader._load_txt(file_path)
            elif suffix == '.pdf' and PDF_AVAILABLE:
                return FileLoader._load_pdf(file_path)
            elif suffix in ['.docx', '.doc'] and DOCX_AVAILABLE:
                return FileLoader._load_docx(file_path)
            else:

                try:
                    return FileLoader._load_txt(file_path)
                except:
                    supported_formats = []
                    if PDF_AVAILABLE:
                        supported_formats.append('.pdf')
                    if DOCX_AVAILABLE:
                        supported_formats.append('.docx/.doc')
                    supported_formats.append('.txt')

                    raise ValueError(
                        f"Неподдерживаемый формат файла: {suffix}. "
                        f"Поддерживаемые форматы: {', '.join(supported_formats)}. "
                        f"Установите соответствующие библиотеки."
                    )
        except Exception as e:
            raise IOError(f"Ошибка при чтении файла {file_path}: {str(e)}")

    @staticmethod
    def _load_txt(file_path: Path) -> str:
        """Загрузка текста из TXT файла."""
        encodings = ['utf-8', 'cp1251', 'koi8-r', 'iso-8859-5']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @staticmethod
    def _load_pdf(file_path: Path) -> str:
        """Загрузка текста из PDF файла."""
        if not PDF_AVAILABLE:
            raise ImportError(
                "PyPDF2 не установлен. Установите его для работы с PDF.")

        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

        return text

    @staticmethod
    def _load_docx(file_path: Path) -> str:
        """Загрузка текста из DOCX файла."""
        if not DOCX_AVAILABLE:
            raise ImportError(
                "python-docx не установлен. Установите его для работы с DOCX.")

        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        return text


class PlagiarismChecker:
    """
    Класс для проверки плагиата.
    """

    def __init__(self,
                 database_dir: str,
                 remove_stopwords: bool = True,
                 lemmatize: bool = True,
                 use_tfidf: bool = True):

        self.database_dir = Path(database_dir)
        self.remove_stopwords = remove_stopwords
        self.lemmatize = lemmatize
        self.use_tfidf = use_tfidf and SKLEARN_AVAILABLE

        if not self.database_dir.exists():
            raise FileNotFoundError(
                f"Директория с базой документов не найдена: {database_dir}")

        self.database_texts = []
        self.database_files = []
        self.preprocessed_database = []

        self._load_database()

    def _load_database(self) -> None:
        """Загрузка и предобработка документов из базы данных."""

        extensions = ['.txt']
        if PDF_AVAILABLE:
            extensions.append('.pdf')
        if DOCX_AVAILABLE:
            extensions.extend(['.docx', '.doc'])

        for ext in extensions:
            files = list(self.database_dir.glob(f'*{ext}'))
            self.database_files.extend(files)

        if not self.database_files:
            warnings.warn(
                f"В директории {self.database_dir} не найдено файлов для сравнения")

        for file_path in self.database_files:
            try:
                text = FileLoader.load_text_from_file(str(file_path))
                preprocessed = TextPreprocessor.preprocess_text(
                    text,
                    remove_stop=self.remove_stopwords,
                    lemmatize=self.lemmatize
                )

                self.database_texts.append(text)
                self.preprocessed_database.append(preprocessed)

            except Exception as e:
                warnings.warn(
                    f"Ошибка при загрузке файла {file_path}: {str(e)}")

    def _calculate_similarity_simple(self, text1: str, text2: str) -> float:

        if not text1 or not text2:
            return 0.0

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union) if union else 0.0

        return similarity

    def _calculate_similarity_tfidf(self, text1: str, text2: str,
                                    all_texts: List[str]) -> float:

        try:

            vectorizer = TfidfVectorizer()

            all_texts_combined = all_texts + [text1, text2]

            tfidf_matrix = vectorizer.fit_transform(all_texts_combined)

            vec1 = tfidf_matrix[-2]
            vec2 = tfidf_matrix[-1]

            similarity = cosine_similarity(vec1, vec2)[0][0]

            similarity = max(0.0, min(1.0, similarity))

            return similarity

        except Exception as e:
            warnings.warn(
                f"Ошибка при расчете TF-IDF: {str(e)}. Используется простой метод.")
            return self._calculate_similarity_simple(text1, text2)

    def check_plagiarism(self, file_to_check: str) -> float:
        try:

            original_text = FileLoader.load_text_from_file(file_to_check)
            preprocessed_text = TextPreprocessor.preprocess_text(
                original_text,
                remove_stop=self.remove_stopwords,
                lemmatize=self.lemmatize
            )

            if not self.preprocessed_database:

                return 100.0

            max_similarity = 0.0

            for db_text in self.preprocessed_database:
                if self.use_tfidf:
                    similarity = self._calculate_similarity_tfidf(
                        preprocessed_text,
                        db_text,
                        self.preprocessed_database + [preprocessed_text]
                    )
                else:
                    similarity = self._calculate_similarity_simple(
                        preprocessed_text,
                        db_text
                    )

                max_similarity = max(max_similarity, similarity)

            originality_percent = (1 - max_similarity) * 100

            originality_percent = max(0.0, min(100.0, originality_percent))

            return round(originality_percent, 2)

        except Exception as e:

            if isinstance(e, (FileNotFoundError, ValueError, IOError)):
                raise
            else:
                raise RuntimeError(f"Ошибка при проверке плагиата: {str(e)}")


def check_document_originality(file_to_check: str, database_dir: str) -> float:
    try:

        if not os.path.exists(file_to_check):
            raise FileNotFoundError(
                f"Файл для проверки не найден: {file_to_check}")

        if not os.path.exists(database_dir):
            raise FileNotFoundError(
                f"Директория с базой документов не найдена: {database_dir}")

        if not os.path.isdir(database_dir):
            raise ValueError(
                f"Указанный путь не является директорией: {database_dir}")

        checker = PlagiarismChecker(
            database_dir=database_dir,
            remove_stopwords=True,
            lemmatize=True,
            use_tfidf=True
        )

        originality = checker.check_plagiarism(file_to_check)

        return originality

    except Exception as e:

        error_msg = str(e)
        if "не найден" in error_msg.lower():
            raise FileNotFoundError(error_msg)
        elif "не является директорией" in error_msg or "формат" in error_msg.lower():
            raise ValueError(error_msg)
        elif "ошибка при чтении" in error_msg.lower() or "ошибка ввода/вывода" in error_msg.lower():
            raise IOError(error_msg)
        else:
            raise RuntimeError(
                f"Ошибка при проверке оригинальности: {error_msg}")
