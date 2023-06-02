from django.contrib import admin
from docgpt.models import DocChatbotFile, DocChatbot, DocChatbotDevice

class DocChatbotFileAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['name', 'active', 'is_deleted']

class DocChatbotAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['name', 'active', 'is_deleted']

class DocChatbotDeviceAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display=['fingerprint']

admin.site.register(DocChatbotFile, DocChatbotFileAdmin)
admin.site.register(DocChatbot, DocChatbotAdmin)
admin.site.register(DocChatbotDevice, DocChatbotDeviceAdmin)