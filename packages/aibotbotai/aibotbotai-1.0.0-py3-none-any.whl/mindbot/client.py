import google.generativeai as genai
from .text import TextGeneration
from .vision import Vision
from .audio import Audio
from .search import Search
from .image import ImageManipulation

class mind:
    _api_key = None

    def __init__(self, api_key=None):
        if api_key:
            mind.config(api_key)
        
        self.text = TextGeneration(self)
        self.vision = Vision(self)
        self.audio = Audio(self)
        self.search = Search(self)
        self.image = ImageManipulation(self)

    @classmethod
    def config(cls, api_key):
        cls._api_key = api_key
        genai.configure(api_key=cls._api_key)
        # Re-initialize the client with the new API key
        cls.client = genai.Client()

    def ask(self, question):
        """A shortcut for basic text generation."""
        if "who are you" in question.lower():
            return "I am MindBot-1.8-ultra, an AI model Developed by Ahmed Helmy Eletr."
        return self.text.generate_content(question)

    def generate_content(self, contents, model="mindbot-1.8-ultra", think=False):
        """A direct interface for text generation, similar to Gemini API."""
        return self.text.generate_content(contents, model=model, think=think)
