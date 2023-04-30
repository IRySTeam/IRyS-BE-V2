class NERResult:
    """
    NERResult class is a class to store the result of named entity recognition.

    [Attributes]
        text: str -> Text that has been processed.
        results: list[dict] -> List of dictionary that contains the result of named entity recognition.
        entities: set[str] -> Set of entities that has been extracted from the text.
    """

    def __init__(self, text, results):
        self.text = text
        self.results = results
        self.entities = {res["entity_group"] for res in results}

    def to_dict(self):
        return self.__dict__()

    def __dict__(self):
        return {
            "text": self.text,
            "results": self.results,
            "entities": list(self.entities),
        }
