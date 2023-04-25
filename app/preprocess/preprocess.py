import string
from collections import defaultdict
from typing import List

from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# WordNetLemmatizer requires Pos tags to understand if the word is noun or verb or adjective etc.
# By default it is set to Noun
tag_map = defaultdict(lambda: wn.NOUN)
tag_map["J"] = wn.ADJ
tag_map["V"] = wn.VERB
tag_map["R"] = wn.ADV


class PreprocessUtil:
    """
    PreprocessUtil is a class that provides several static methods to preprocess text using NLTK.
    """

    lemmatizer = WordNetLemmatizer()
    list_stopword = set(stopwords.words("english"))

    @classmethod
    def case_folding(cls, text: str) -> str:
        """
        Function to convert text to lowercase.
        [Parameters]
            text: str -> Text to be preprocessed.
        [Returns]
            str: Text in lowercase.
        """
        return text.lower()

    @classmethod
    def punctuation_removal(cls, text: str) -> str:
        """
        Function to remove punctuation from a text.
        [Parameters]
            text: str -> Text to be preprocessed.
        [Returns]
            str: Text without punctuation.
        """
        return text.translate(str.maketrans("", "", string.punctuation))

    @classmethod
    def remove_stopwords(cls, words: List[str]) -> List[str]:
        """
        Function to remove stopwords from a list of words.
        [Parameters]
            words: List[str] -> List of words.
        [Returns]
            List[str]: List of words without stopwords.
        """
        return [word for word in words if word not in cls.list_stopword]

    @classmethod
    def stem_words(cls, words: List[str]) -> List[str]:
        """
        Function to reduce words to their root form while maintaining the context (lemmatization)
        from a list of words.
        [Parameters]
            words: List[str] -> List of words.
        [Returns]
            List[str]: List of words reduced to their root form.
        """
        return [
            cls.lemmatizer.lemmatize(word, tag_map[tag[0]])
            for word, tag in pos_tag(words)
        ]

    @classmethod
    def preprocess(cls, text: str) -> List[str]:
        """
        Function to preprocess text.
        [Parameters]
            text: str -> Text to be preprocessed.
        [Returns]
            List[str]: List of preprocessed words.
        """

        # Do preprocessing.
        text = cls.case_folding(text)
        text = cls.punctuation_removal(text)
        text = text.strip()
        text = word_tokenize(text)
        text = cls.remove_stopwords(text)
        text = cls.stem_words(text)

        return text
