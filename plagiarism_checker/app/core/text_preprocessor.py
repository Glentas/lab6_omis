import re
import string
from typing import List, Optional
import warnings


class TextPreprocessor:
    """
    Класс для предобработки русских текстов.
    """

    RUSSIAN_STOPWORDS = {
        'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а',
        'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же',
        'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от',
        'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже',
        'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был',
        'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь',
        'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут',
        'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем',
        'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже',
        'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того',
        'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом',
        'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были',
        'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец',
        'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот',
        'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много',
        'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой',
        'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой',
        'им', 'более', 'всегда', 'конечно', 'всю', 'между'
    }

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Нормализация текста: приведение к нижнему регистру, удаление лишних пробелов.
        """
        if not text or not isinstance(text, str):
            return ""

        text = text.lower()

        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    @staticmethod
    def remove_punctuation(text: str) -> str:
        """
        Удаление пунктуации из текста.
        """
        if not text:
            return ""

        translator = str.maketrans('', '', string.punctuation + '«»„“"\'')
        text = text.translate(translator)

        return text

    @staticmethod
    def remove_numbers(text: str) -> str:
        """
        Удаление чисел из текста.
        """
        if not text:
            return ""

        text = re.sub(r'\d+', '', text)
        return text

    @staticmethod
    def remove_stopwords(text: str, custom_stopwords: Optional[set] = None) -> str:

        if not text:
            return ""

        stopwords = TextPreprocessor.RUSSIAN_STOPWORDS.copy()
        if custom_stopwords:
            stopwords.update(custom_stopwords)

        words = text.split()

        filtered_words = [word for word in words if word not in stopwords]

        return ' '.join(filtered_words)

    @staticmethod
    def lemmatize_text(text: str) -> str:

        if not text:
            return ""

        lemmatization_rules = {
            'ать': 'а',
            'ять': 'я',
            'еть': 'е',
            'ить': 'и',
            'ться': 'ть',
            'тся': 'ть',
            'ого': 'ий',
            'его': 'ий',
            'ым': 'ый',
            'им': 'ий',
            'ом': '',
            'ем': '',
            'ых': 'ый',
            'их': 'ий',
            'ую': 'ый',
            'юю': 'ий',
            'ая': 'ый',
            'яя': 'ий',
            'ое': 'ый',
            'ее': 'ий',
            'ии': 'ия',
            'ые': 'ый',
            'ие': 'ий'
        }

        words = text.split()
        lemmatized_words = []

        for word in words:

            lemma = word
            for suffix, replacement in lemmatization_rules.items():
                if word.endswith(suffix):
                    lemma = word[:-len(suffix)] + replacement
                    break

            lemmatized_words.append(lemma)

        return ' '.join(lemmatized_words)

    @classmethod
    def preprocess_text(cls, text: str,
                        remove_stop: bool = True,
                        lemmatize: bool = True,
                        custom_stopwords: Optional[set] = None) -> str:

        if not text:
            return ""

        try:

            processed_text = cls.normalize_text(text)

            processed_text = cls.remove_punctuation(processed_text)

            processed_text = cls.remove_numbers(processed_text)

            if remove_stop:
                processed_text = cls.remove_stopwords(
                    processed_text, custom_stopwords)

            if lemmatize:
                processed_text = cls.lemmatize_text(processed_text)

            processed_text = re.sub(r'\s+', ' ', processed_text)
            processed_text = processed_text.strip()

            return processed_text

        except Exception as e:
            warnings.warn(f"Ошибка при предобработке текста: {str(e)}")
            return text
