from django.conf import settings
from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from chatbot.models import Chatbot
from chatbot.serializers import ChatbotFileSerializer, ChatbotSerializer, ChatbotFetchSerializer
from chatbot.aws import S3, getS3BucketKey

from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
# Create your views here.

class ChatbotFileView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        fileName = request.data['fileName']
        serializer = ChatbotFileSerializer(data={ 'name': fileName })
        if serializer.is_valid():
            obj = serializer.save()

            key = getS3BucketKey(obj.id, fileName)
            url = S3().get_presigned_url(key)
            pUrl = f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{key}"

            obj.url = pUrl
            obj.save()
            return Response({ 'sUrl': url, 'fileId': obj.id, 'pUrl': pUrl }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatbotView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        chatbots = Chatbot.objects.filter(user=request.user)
        serializer = ChatbotFetchSerializer(chatbots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        request.data['user'] = request.user.id
        serializer = ChatbotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatView(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self, request, id):
        try:
            return Chatbot.objects.get(pk=id, user=request.user)
        except Chatbot.DoesNotExist:
            raise Http404

    def conversational_chat(self, query, uploaded_file):
        csv_agent = create_csv_agent(OpenAI(temperature=0), uploaded_file, verbose=False)
        try:
            response= csv_agent.run(query)
        except Exception as e:
            response = str(e)
            if response.startswith("Could not parse LLM output: `"):
                response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
        return response

    def get(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        serializer = ChatbotFetchSerializer(chatbot)
        chat = [{ "role": "assistant", "content": "Hi! What can I help you with?" }]
        return Response({ "chat": chat, "chatbot": serializer.data, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit }, status=status.HTTP_200_OK)
    
    def post(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        chat = request.data['chat']
        last_chat = chat.pop()
        if chatbot.question_limit < settings.CHATBOT_QUESTION_LIMIT:
            chat_response = self.conversational_chat(last_chat['content'], chatbot.file_urls.all()[0].url)
            chatbot.question_limit += 1
            chatbot.save()
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit  }, status=status.HTTP_200_OK)
        return Response({ "message": "You reached maximum chat question limit" }, status=status.HTTP_400_BAD_REQUEST)