import os
import google.generativeai as genai

class GeminiEmbedding:
    def __init__(self, model_name="models/embedding-001"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def embed_text(self, text):
        # Gemini API expects a list of texts
        response = self.model.embed_content([text])
        return response['embedding']

    def embed_texts(self, texts):
        response = self.model.embed_content(texts)
        return [item['embedding'] for item in response['embeddings']] 