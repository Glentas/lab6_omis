import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from typing import List, Tuple, Dict, Any
import string

# Загрузка ресурсов NLTK (при первом запуске)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

class TextProcessor:
    """Процессор для обработки текста"""
    
    def __init__(self, language: str = 'russian'):
        self.language = language
        self.stop_words = set(stopwords.words('russian') + stopwords.words('english'))
        
    def normalize_text(self, text: str) -> str:
        """Нормализация текста"""
        # Приведение к нижнему регистру
        text = text.lower()
        
        # Удаление лишних пробелов
        text = ' '.join(text.split())
        
        # Удаление пунктуации (опционально, можно закомментировать)
        # text = text.translate(str.maketrans('', '', string.punctuation))
        
        return text
    
    def remove_stop_words(self, text: str) -> str:
        """Удаление стоп-слов"""
        words = word_tokenize(text, language=self.language)
        filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
        return ' '.join(filtered_words)
    
    def tokenize_text(self, text: str) -> List[str]:
        """Токенизация текста"""
        return word_tokenize(text, language=self.language)
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Разделение текста на предложения"""
        return sent_tokenize(text, language=self.language)
    
    def extract_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Извлечение N-грамм из текста"""
        tokens = self.tokenize_text(text)
        ngrams = []
        
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def calculate_text_metrics(self, text: str) -> Dict[str, Any]:
        """Вычисление метрик текста"""
        words = self.tokenize_text(text)
        sentences = self.split_into_sentences(text)
        
        return {
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }


class SimilarityCalculator:
    """Калькулятор схожести текстов"""
    
    @staticmethod
    def calculate_cosine_similarity(text1: str, text2: str) -> float:
        """Вычисление косинусной схожести"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]
    
    @staticmethod
    def calculate_jaccard_similarity(text1: str, text2: str) -> float:
        """Вычисление коэффициента Жаккара"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0
    
    @staticmethod
    def find_exact_matches(source_text: str, target_text: str, min_length: int = 20) -> List[Dict[str, Any]]:
        """Поиск точных совпадений"""
        matches = []
        source_words = source_text.split()
        target_words = target_text.split()
        
        for i in range(len(source_words) - min_length + 1):
            for j in range(len(target_words) - min_length + 1):
                match_length = 0
                
                while (i + match_length < len(source_words) and 
                       j + match_length < len(target_words) and 
                       source_words[i + match_length] == target_words[j + match_length]):
                    match_length += 1
                
                if match_length >= min_length:
                    matched_text = ' '.join(source_words[i:i + match_length])
                    matches.append({
                        'source_position': i,
                        'target_position': j,
                        'length': match_length,
                        'text': matched_text,
                        'similarity': 1.0
                    })
        
        return matches
    
    @staticmethod
    def find_similar_fragments(source_text: str, target_text: str, 
                               threshold: float = 0.8, 
                               fragment_size: int = 50) -> List[Dict[str, Any]]:
        """Поиск схожих фрагментов"""
        matches = []
        
        source_sentences = re.split(r'[.!?]+', source_text)
        target_sentences = re.split(r'[.!?]+', target_text)
        
        for i, source_sent in enumerate(source_sentences):
            if len(source_sent.strip()) < fragment_size:
                continue
                
            for j, target_sent in enumerate(target_sentences):
                if len(target_sent.strip()) < fragment_size:
                    continue
                
                similarity = SimilarityCalculator.calculate_cosine_similarity(
                    source_sent.strip(), target_sent.strip()
                )
                
                if similarity >= threshold:
                    matches.append({
                        'source_sentence_idx': i,
                        'target_sentence_idx': j,
                        'source_fragment': source_sent.strip(),
                        'target_fragment': target_sent.strip(),
                        'similarity': similarity
                    })
        
        return matches
