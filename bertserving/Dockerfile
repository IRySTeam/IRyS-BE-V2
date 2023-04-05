FROM tensorflow/tensorflow:1.12.0-py3

RUN pip install -U pip

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -U bert-serving-server bert-serving-client

COPY ./ /app

COPY ./entrypoint.sh /app

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]

CMD []
