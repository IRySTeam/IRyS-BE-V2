FROM python:3.10

COPY . /home

WORKDIR /home
RUN apt-get update && apt-get install -y --no-install-recommends \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  # Apache Tika dependencies
  openjdk-11-jdk ant ca-certificates-java \
  # pdf2image dependencies
  poppler-utils \
  # pytesseract dependencies
  tesseract-ocr \
  # python-magic dependencies
  libmagic1 \
  # CV dependencies
  ffmpeg libsm6 libxext6  \
  # Additional dependencies
  telnet netcat \
  # Fix java certificate issues
  && apt-get clean \
  && update-ca-certificates -f \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry"

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

RUN python -m nltk.downloader punkt wordnet stopwords averaged_perceptron_tagger

RUN python app/classification/mlutil/classifier_training.py

EXPOSE 8000

CMD ["python3", "main.py"]
