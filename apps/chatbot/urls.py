from django.urls import path
from chatbot.views import ChatbotView, ChatbotFileView, ChatView, ChatbotDemoView, DemoChatView


app_name = 'chatbot'
urlpatterns = [
    path('', ChatbotView.as_view(), name="csv_chat_bot"),
    path('demo/', ChatbotDemoView.as_view(), name="demo_csv_bot_chat"),
    path('signedurl/', ChatbotFileView.as_view(), name="file_signed_url"),
    path('<int:id>/chat/', ChatView.as_view(), name="bot_chat"),
    path('<int:id>/demo/chat/', DemoChatView.as_view(), name="demo_bot_chat"),
]