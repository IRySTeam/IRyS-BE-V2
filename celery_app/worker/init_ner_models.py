import os

from transformers import pipeline

from app.extraction.configuration import NER_MODELS

base_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)

# Get app/extraction path
model_base_path = os.path.join(base_path, "app", "extraction", "domains")

for domain, model in NER_MODELS.items():
    print(f"Downloading model {model} for {domain} domain")
    # Construct model path
    model_path = os.path.join(model_base_path, domain, "ner_model")

    # Download
    pipe = pipeline("token-classification", model=model, aggregation_strategy="simple")
    pipe.save_pretrained(model_path)

print("NER models downloaded")
