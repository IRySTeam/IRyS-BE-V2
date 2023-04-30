FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

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

# Requirements are installed here to ensure they will be cached.
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Create log file for tika and give permissions, /var/log/tika.log
RUN touch /var/log/tika.log \
    && chmod 777 /var/log/tika.log

# # Install poetry and dependencies.
# COPY ./pyproject.toml /pyproject.toml
# RUN pip install "poetry" \
#     && poetry config virtualenvs.create false \
#     && poetry install --only main

# Download nltk data
RUN python -m nltk.downloader punkt wordnet stopwords averaged_perceptron_tagger

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME

# Celery worker
COPY ./celery_app/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker \
    && chmod +x /start-celeryworker

# Celery beat
COPY ./celery_app/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat \
    && chmod +x /start-celerybeat

# Celery flower
COPY ./celery_app/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower \
    && chmod +x /start-flower

WORKDIR /app
