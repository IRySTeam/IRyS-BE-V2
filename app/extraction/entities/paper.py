import nltk
from app.extraction.entities.base import NER
from app.extraction.nerresult import NERResult

class PaperNER(NER):
  """
  PaperNER class is a class for paper domain named entity recognition.
  
  [Attributes]
    pipeline: Pipeline -> Huggingface NER pipeline.
  """
  def __init__(self, model_name:str = "topmas/IRyS-NER-Paper") -> None:
    """
    Constructor of PaperNER class

    [Arguments]
        model_name: str -> Name of the model on huggingface. Defaults to "topmas/IRyS-NER-Paper".
    """

    super().__init__(model_name)

  def preprocess(self, text:str) -> list[str]:
    """
    Preprocess text for paper domain

    [Arguments]
        text: str -> Text to preprocess
    """

    headers = []
    textsplit = text.splitlines()

    for idx, line in enumerate(textsplit):
        if "Abstract" in line or idx == 20:
            break
        headers.append(line)

    header = "\n".join(headers)
    body = "\n".join(textsplit[idx:])

    preprocessed = nltk.sent_tokenize(body)
    preprocessed = [header] + [sent.replace("\n", " ") for sent in preprocessed]

    return preprocessed

  def extract(self, text:str) -> NERResult:
    """
    Extract entities from text

    [Arguments]
        text: str -> Text to extract entities from
    """

    preprocessed = self.preprocess(text)
    ner_results = [self.pipeline(sent) for sent in preprocessed]
    
    full_text = "".join(preprocessed)

    result = []
    cur_len = 0
    for idx, sent in enumerate(preprocessed):
        sent_len = len(sent)
        for ner in ner_results[idx]:
            ner["start"] += cur_len
            ner["end"] += cur_len
        cur_len += sent_len 
        result += ner_results[idx]
 
    return NERResult(full_text, result)