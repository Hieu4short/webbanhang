from transformers import pipeline
import torch
from .chat_response import get_response, RESPONSES
from django.apps import apps

class ChatbotService:
    def __init__(self):
        self.model = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            device_map="auto",          
            torch_dtype=torch.float16  
        )

    def get_response(self, user_input):
        response = get_response(user_input)
        if response != RESPONSES["default"]:
            return response
        

        Article = apps.get_model('app', 'Article')
        articles = Article.objects.filter(title__icontains=user_input)[:3]

        if articles.exists():
            titles = "\n- ".join(a.title for a in articles)
            return f"I just found {articles.count()} relevant articles:\n- {titles}\n\nSee detail at Articles!"
        
        return RESPONSES["default"]

chatbot = ChatbotService()