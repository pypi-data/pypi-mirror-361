import google.generativeai as genai
from .text import TextGeneration
from .vision import Vision
from .audio import Audio
from .search import Search
from .image import ImageManipulation

class mind:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.client = genai.Client()

        self.text = TextGeneration(self)
        self.vision = Vision(self)
        self.audio = Audio(self)
        self.search = Search(self)
        self.image = ImageManipulation(self)

    def ask(self, question):
        """A shortcut for basic text generation."""
        if "who are you" in question.lower():
            return "I am MindBot-1.8-ultra, an AI model Developed by Ahmed Helmy Eletr."
        return self.text.generate_content(question)
