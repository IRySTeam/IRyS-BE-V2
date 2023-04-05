import os
import pickle
from typing import List, Dict
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

path = os.path.join(os.getcwd(), "app", "classification", "dump")
labelencode_name = "labelencoder_fitted.pkl"
tfidf_vect_name = "tfidf_vect_fitted.pkl"
svm_name = "svm_trained_model.sav"

class Classifier:
    """
    Classifier is a class that provides several static methods to classify text using SVM.
    """
    labelencode: LabelEncoder = pickle.load(open(os.path.join(path, labelencode_name), 'rb'))
    tfidf_vect: TfidfVectorizer = pickle.load(open(os.path.join(path, tfidf_vect_name), 'rb'))
    svm: SVC = pickle.load(open(os.path.join(path, svm_name), 'rb'))
    label_mapping: Dict[str, str] = {
        "__other__": "General Document (Not Classified)",
        "__resume__": "Recruitment Document",
        "__paper__": "Scientific Document",
    }
    
    @classmethod
    def classify(cls, texts: List[str]) -> str:
        """
        Classify texts using SVM.
        [Parameters]
            texts: List[str] -> Texts that has been preprocessed. 
        [Returns]
            str: Label of the text.
        """
        texts = str(texts)
        texts_vectorized = cls.tfidf_vect.transform([texts])
        prediction = cls.svm.predict(texts_vectorized)
        return cls.labelencode.inverse_transform(prediction)[0]
    
    @classmethod
    def label_to_doc_category(cls, label: str) -> str:
        """
        Get document category from label.
        [Parameters]
            label: str -> Label of the text.
        [Returns]
            str: Document category.
        """
        return cls.label_mapping[label]