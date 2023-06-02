from rest_framework import serializers
from docgpt.models import DocChatbotFile, DocChatbot
from chatbot.aws import S3

class DocChatbotFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocChatbotFile
        fields = '__all__'


class DocChatbotSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocChatbot
        fields = '__all__'


class DocChatbotFetchSerializer(serializers.ModelSerializer):
    file_urls = DocChatbotFileSerializer(many=True, read_only=True)
    bot_logo = DocChatbotFileSerializer(read_only=True)
    class Meta:
        model = DocChatbot
        fields = '__all__'