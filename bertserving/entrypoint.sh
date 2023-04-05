#!/bin/sh

# Check if /model is exists. If not, create it.
if [ ! -d "/model" ]; then
    mkdir /model
fi

# Check if /model is empty. If so, try to download the model or use the model if exists.
if [ -z "$(ls -A /model)" ]; then
    # Check model directory exists using $MODEL_NAME
    if [ ! -d "$MODEL_NAME" ]; then
        echo "Model not found. Downloading..."
        wget $MODEL_DOWNLOAD_URL
        unzip $MODEL_NAME.zip
    else
        echo "Using existing model," $MODEL_NAME
    fi
    cp -r $MODEL_NAME/* /model
fi

bert-serving-start -num_worker=1 -max_seq_len=256 -model_dir /model
