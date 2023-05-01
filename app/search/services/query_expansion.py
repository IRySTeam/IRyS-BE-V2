from transformers import pipeline

class QueryExpansionService:
    def __init__(self, model):
        """
        Constructor of QueryExpansionService class
        """
        self.generator = pipeline(
            'text-generation', tokenizer='gpt2', model=model
        )

        self.expansion_method = {
            "basic": self.basic_generator,
            "beam": self.beam_generator,
            "random_sampling": self.random_sampling_generator,
            "k_sampling": self.k_sampling_generator,
            "p_sampling": self.p_sampling_generator
        }

    def basic_generator(self, query: str):
        n = len(query.split()) + 10
        return self.generator(query, max_length=n)[0]['generated_text']
    
    def beam_generator(self, query: str):
        n = len(query.split()) + 10
        return self.generator(
            query,
            max_length=n,
            num_beams=5
        )[0]['generated_text']
    
    def random_sampling_generator(self, query: str):
        n = len(query.split()) + 10
        return self.generator(
            query,
            max_length=n,
            top_k=0,
            do_sample=True,
            temperature=0.7
        )[0]['generated_text']
    
    def k_sampling_generator(self, query: str):
        n = len(query.split()) + 10
        return self.generator(
            query,
            max_length=n,
            top_k=40,
            do_sample=True
        )[0]['generated_text']
    
    def p_sampling_generator(self, query: str):
        n = len(query.split()) + 10
        return self.generator(
            query,
            max_length=n,
            top_k=0,
            top_p=0.92,
            do_sample=True
        )[0]['generated_text']