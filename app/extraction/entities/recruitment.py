import nltk
from app.extraction.entities.base import NER
from app.extraction.nerresult import NERResult

class RecruitmentNER(NER):
  """
  RecruitmentNER class is a class for recruitment domain named entity recognition.
  
  [Attributes]
    pipeline: Pipeline -> Huggingface NER pipeline.
  """

  def __init__(self, model_name:str = "topmas/IRyS-NER-Recruitment") -> None:
    """
    Constructor of RecruitmentNER class

    [Arguments]
        model_name: str -> Name of the model on huggingface. Defaults to "topmas/IRyS-NER-Recruitment".
    """

    super().__init__(model_name)

  def preprocess(self, text:str) -> str:
    """
    Preprocess text for recruitment domain

    [Arguments]
        text: str -> Text to preprocess
    """

    return text.replace("\n", " ")

  def extract(self, text:str) -> NERResult:
    """
    Extract entities from text

    [Arguments]
        text: str -> Text to extract entities from
    """

    preprocessed = self.preprocess(text)
    ner_result = self.pipeline(preprocessed)

    return NERResult(text, ner_result)
