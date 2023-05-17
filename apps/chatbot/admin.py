from django.contrib import admin
from chatbot.models import ChatbotFile, Chatbot

class ChatbotFileAdmin(admin.ModelAdmin):
    list_per_page = 100

class ChatbotAdmin(admin.ModelAdmin):
    list_per_page = 100

admin.site.register(ChatbotFile, ChatbotFileAdmin)
admin.site.register(Chatbot, ChatbotAdmin)