from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

class TextEncodingService:

    encoder_mapping = {
        "general": "salsabiilashifa11/sbert-paper",
        "scientific": "salsabiilashifa11/sbert-paper",
        "recruitment": "salsabiilashifa11/sbert-paper",
    }

    def __init__(self, domain: str = "general"):
        """
        Constructor of TextEncodingService class
        """
        if domain not in self.encoder_mapping:
            domain = "general"

        self.encoder = AutoModel.from_pretrained(self.encoder_mapping[domain])
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')
        
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, query: str):
        encoded_input = self.tokenizer([query], padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self.encoder(**encoded_input)
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings[0].numpy().tolist()
