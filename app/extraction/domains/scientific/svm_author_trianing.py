import os
import pickle

import pandas as pd
from imblearn.over_sampling import SMOTENC
from sklearn import model_selection, svm
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

dir_path = os.path.dirname(os.path.realpath(__file__))
training_data_path = os.path.join(dir_path, "training_data.json")

df = pd.read_json(training_data_path)

X = df.drop(columns="sentiment")
y = df["sentiment"]

# Split dataset into train and test
train_X, test_X, train_y, test_y = model_selection.train_test_split(X, y, test_size=0.2)

num_col = [
    "caps_count",
    "at_count",
    "num_count",
    "affiliation_count",
    "comma_count",
    "comma_percent",
    "punct_count",
    "punct_percent",
]
cat_col = [
    "label",
    "prev_label",
    "next_label",
    "same_characteristic_prev",
    "same_characteristic_next",
]

# Create pipeline for classifier
numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])

categorical_transformer = Pipeline(
    steps=[("encoder", OneHotEncoder(handle_unknown="ignore"))]
)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, num_col),
        ("cat", categorical_transformer, cat_col),
    ]
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", svm.SVC(kernel="rbf", gamma=0.1, C=100)),
    ]
)

# Oversample training data
sm = SMOTENC(random_state=None, categorical_features=[0, 9, 10, 11, 12])
train_X, train_y = sm.fit_resample(train_X, train_y)

pipeline.fit(train_X, train_y)

print("SVM Classifier score:", pipeline.score(test_X, test_y))

# Save model
model_path = os.path.join(dir_path, "dump", "svm_author_classifier.pkl")
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)

print("Files saved to disk")
