from django.contrib import admin
from chatbot.models import ChatbotFile, Chatbot

class ChatbotFileAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['name', 'active', 'is_deleted']

class ChatbotAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['name', 'active', 'is_deleted']

admin.site.register(ChatbotFile, ChatbotFileAdmin)
admin.site.register(Chatbot, ChatbotAdmin)