from django.urls import path
from chatbot.views import ChatbotView, ChatbotFileView, ChatView


app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotView.as_view(), name="csv_chat_bot"),
    path('signedurl/', ChatbotFileView.as_view(), name="file_signed_url"),
    path('<int:id>/chat/', ChatView.as_view(), name="bot_chat"),
]