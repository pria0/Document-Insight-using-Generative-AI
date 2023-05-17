from rest_framework import serializers
from chatbot.models import ChatbotFile, Chatbot
from chatbot.aws import S3

class ChatbotFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatbotFile
        fields = '__all__'


class ChatbotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chatbot
        fields = '__all__'


class ChatbotFetchSerializer(serializers.ModelSerializer):
    file_urls = ChatbotFileSerializer(many=True, read_only=True)
    class Meta:
        model = Chatbot
        fields = '__all__'