FROM python:3.10

COPY . /home

WORKDIR /home

RUN pip install "poetry"

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

RUN python3 -m nltk.downloader corpora

EXPOSE 8000

CMD ["python3", "main.py"]
