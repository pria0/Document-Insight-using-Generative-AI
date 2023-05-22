from django.contrib import admin
from chatbot.models import ChatbotFile, Chatbot, ChatbotDevice

class ChatbotFileAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['name', 'active', 'is_deleted']

class ChatbotAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['name', 'active', 'is_deleted']

class ChatbotDeviceAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['fingerprint']

admin.site.register(ChatbotFile, ChatbotFileAdmin)
admin.site.register(Chatbot, ChatbotAdmin)
admin.site.register(ChatbotDevice, ChatbotDeviceAdmin)