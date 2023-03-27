from transformers import pipeline
from app.extraction.nerresult import NERResult

class NER:
    """
    NER class is a base class for general domain named entity recognition 
    and can be extended for more specific domain.

    [Attributes]
    pipeline: Pipeline -> Huggingface NER pipeline.
    """

    def __init__(self, model_name:str = "dslim/bert-base-NER"):
        """
        Constructor of NER class

        [Arguments]
            model_name: str -> Name of the model on huggingface. Defaults to "dslim/bert-base-NER".
        """

        self.pipeline = pipeline("ner", model=model_name, aggregation_strategy="first")

    def preprocess(self, text:str) -> str|list[str]:
        """
        Preprocess text for general domain

        [Arguments]
            text: str -> Text to preprocess
        """

        return text

    def extract(self, text:str) -> NERResult:
        """
        Extract entities from text

        [Arguments]
            text: str -> Text to extract entities from
        """

        preprocessed = self.preprocess(text)
        ner_result = self.pipeline(preprocessed)
        return ner_result