from app.search.services.text_encoding import TextEncodingService

class TextEncodingManager:

    def __init__(self):
        """
        Constructor of TextEncodingManager class
        """
        self.general_encoder = TextEncodingService()
        self.recruitment_encoder = TextEncodingService('recruitment')
        self.scientific_encoder = TextEncodingService('scientific')

    def get_encoder(self, domain: str = 'general'):
        match domain:
            case 'recruitment':
                return self.recruitment_encoder
            case 'scientific':
                return self.scientific_encoder
            case _:
                return self.general_encoder