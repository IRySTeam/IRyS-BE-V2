import os
import pickle
import string
from collections import defaultdict

import numpy as np
import pandas as pd
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn import model_selection, svm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Set Random seed
np.random.seed(500)

# Add the Data using pandas
corpus_path = os.path.join(
    os.getcwd(), "app", "classification", "mlutil", "classifier_corpus.csv"
)
corpus = pd.read_csv(corpus_path, encoding="latin-1")

# WordNetLemmatizer requires Pos tags to understand if the word is noun or verb or adjective etc. By default it is set to Noun
tag_map = defaultdict(lambda: wn.NOUN)
tag_map["J"] = wn.ADJ
tag_map["V"] = wn.VERB
tag_map["R"] = wn.ADV


def text_preprocessing(text):
    # Change all the text to lower case. This is required as python interprets
    # 'dog' and 'DOG' differently
    if type(text) != str:
        text = str(text)
    text = text.lower()

    # Punctuation removal
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenization : In this each entry in the corpus will be broken into set of words
    text_words_list = word_tokenize(text)

    # Remove Stop words, Non-Numeric and perfom Word Stemming/Lemmenting.
    Final_words = []
    word_Lemmatized = WordNetLemmatizer()
    # pos_tag function below will provide the 'tag' i.e if the word is Noun(N) or Verb(V) or
    # something else.
    for word, tag in pos_tag(text_words_list):
        # Below condition is to check for Stop words and consider only alphabets
        if word not in stopwords.words("english") and word.isalpha():
            word_Final = word_Lemmatized.lemmatize(word, tag_map[tag[0]])
            Final_words.append(word_Final)
    return str(Final_words)


def training():
    # Data Pre-processing - This will help in getting better results through the classification algorithms

    # Remove blank rows if any.
    corpus["text"].dropna(inplace=True)
    corpus["text_final"] = corpus["text"].map(text_preprocessing)

    # Split the model into Train and Test Data set.
    Train_X, Test_X, Train_Y, Test_Y = model_selection.train_test_split(
        corpus["text_final"], corpus["label"], test_size=0.3
    )

    # Step - 3: Label encode the target variable  - This is done to transform Categorical data of
    # string type in the data set into numerical values
    Encoder = LabelEncoder()
    Encoder.fit(Train_Y)
    Train_Y = Encoder.transform(Train_Y)
    Test_Y = Encoder.transform(Test_Y)

    # Step - 4: Vectorize the words by using TF-IDF Vectorizer - This is done to find how important
    # a word in document is in comaprison to the corpus
    # Tfidf_vect = TfidfVectorizer(max_features=5000)
    Tfidf_vect = TfidfVectorizer()
    Tfidf_vect.fit(corpus["text_final"])

    Train_X_Tfidf = Tfidf_vect.transform(Train_X)
    Test_X_Tfidf = Tfidf_vect.transform(Test_X)

    # Classifier - Algorithm - SVM
    SVM = svm.SVC(C=1.0, kernel="linear", degree=3, gamma="auto", probability=True)
    SVM.fit(Train_X_Tfidf, Train_Y)
    predictions_SVM = SVM.predict(Test_X_Tfidf)
    print("SVM Accuracy Score -> ", accuracy_score(predictions_SVM, Test_Y) * 100)

    # Saving Encoder, TFIDF Vectorizer and the trained model for future infrerencing/prediction.
    path = os.path.join(os.getcwd(), "app", "classification", "dump")
    filename = os.path.join(path, "labelencoder_fitted.pkl")
    pickle.dump(Encoder, open(filename, "wb"))
    filename = os.path.join(path, "tfidf_vect_fitted.pkl")
    pickle.dump(Tfidf_vect, open(filename, "wb"))
    filename = os.path.join(path, "svm_trained_model.sav")
    pickle.dump(SVM, open(filename, "wb"))

    print("Files saved to disk")


if __name__ == "__main__":
    training()
