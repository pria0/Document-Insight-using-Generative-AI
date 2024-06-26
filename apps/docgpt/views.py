import os
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from docgpt.models import DocChatbot, DocChatbotDevice, DocChatbotFile
from docgpt.serializers import DocChatbotFileSerializer, DocChatbotSerializer, DocChatbotFetchSerializer

from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS

from docgpt.core import run_llm

class DocgptFileView(APIView):

    def post(self, request):
        requestFile = request.FILES.get('uploadFile')
        serializer = DocChatbotFileSerializer(data={ 'name': requestFile.name, 'file': requestFile })
        if serializer.is_valid():
            obj = serializer.save()
            obj.url = obj.file.url
            obj.save()
            return Response({ 'sUrl': obj.file.url, 'fileId': obj.id, 'pUrl': obj.file.url }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocgptbotView(APIView):
    permission_classes = ()

    def get(self, request, format=None):
        if request.user.is_superuser:
            chatbots = DocChatbot.objects.isActive().filter(user=request.user)
        else:
            chatbots = DocChatbot.objects.isActive().filter(is_demo=False)
        serializer = DocChatbotFetchSerializer(chatbots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def train_model(self, chatbot_data):
        if chatbot_data:
            files = DocChatbotFile.objects.filter(id__in=chatbot_data['file_urls'])
            urls = [f"{settings.LOCAL_HOST_PORT}{file.url}" for file in files]
            loader = UnstructuredURLLoader(urls=urls)
            data = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=400, chunk_overlap=50, separators=["\n\n", "\n", " ", ""]
            )
            documents = text_splitter.split_documents(data)
            embeddings = OpenAIEmbeddings()
            vectorstore = FAISS.from_documents(documents, embeddings)
            vectorstore.save_local(f"faiss_index_{chatbot_data['id']}")
    
    def post(self, request, format=None):
        serializer = DocChatbotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.train_model(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocgptbotDemoView(APIView):
    def post(self, request, format=None):
        fingerprint = request.data['fingerprint'] if 'fingerprint' in request.data.keys() else ''
        chatbots = DocChatbot.objects.isActive().filter(is_demo=True)
        serializer = DocChatbotFetchSerializer(chatbots, many=True)
        for chatbot in chatbots:
            obj, created = DocChatbotDevice.objects.update_or_create(fingerprint=fingerprint, chatbot=chatbot)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DemoDocChatView(APIView):

    def get_object(self, request, id):
        try:
            return DocChatbot.objects.isActive().get(pk=id, is_demo=True)
        except DocChatbot.DoesNotExist:
            raise Http404
    
    def create_chat_history(self, chat):
        chat_prompt = [c['content'] for c in chat if c['role'] == 'user']
        chat_answer = [c['content'] for c in chat if c['role'] == 'assistant']
        return list(zip(chat_prompt, chat_answer))

    def conversational_chat(self, query, chatbot_id, chat_history):
        response = run_llm(query, f"faiss_index_{chatbot_id}", chat_history)
        return response['answer']

    def get(self, request, id, format=None):
        fingerprint = request.GET.get('fingerprint', '')
        if not DocChatbotDevice.objects.filter(fingerprint=fingerprint, chatbot__id=id).exists():
            return Response({ "status": status.HTTP_400_BAD_REQUEST, "message": "Device fingerprint not matched" }, status=status.HTTP_200_OK)
        chatbot = self.get_object(request, id)
        serializer = DocChatbotFetchSerializer(chatbot)
        chat = [{ "role": "assistant", "content": "Hi! 👋 What can I help you with?" }]
        chatbot_data = serializer.data

        chatbot_device = DocChatbotDevice.objects.get(fingerprint=fingerprint, chatbot__id=id)

        return Response({ "chat": chat, "chatbot": chatbot_data, "is_api_key_set": False, "question_limit": settings.DEMO_CHATBOT_QUESTION_LIMIT - chatbot_device.question_limit }, status=status.HTTP_200_OK)
    
    def post(self, request, id, format=None):
        fingerprint = request.data['fingerprint'] if 'fingerprint' in request.data.keys() else ''
        if not DocChatbotDevice.objects.filter(fingerprint=fingerprint, chatbot__id=id).exists():
            return Response({ "status": status.HTTP_400_BAD_REQUEST, "message": "Device fingerprint not matched" }, status=status.HTTP_200_OK)
        chatbot = self.get_object(request, id)
        chat = request.data['chat']
        last_chat = chat.pop()

        chatbot_device = DocChatbotDevice.objects.get(fingerprint=fingerprint, chatbot__id=id)
        if chatbot_device.question_limit < settings.DEMO_CHATBOT_QUESTION_LIMIT:
            chat_history = self.create_chat_history(chat[1:])
            print(chat_history)
            chat_response = self.conversational_chat(last_chat['content'], chatbot.id, chat_history)
            chatbot_device.question_limit += 1
            chatbot_device.save()
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": False, "question_limit": settings.DEMO_CHATBOT_QUESTION_LIMIT - chatbot_device.question_limit  }, status=status.HTTP_200_OK)
        return Response({ "status": status.HTTP_400_BAD_REQUEST, "question_limit": settings.DEMO_CHATBOT_QUESTION_LIMIT - chatbot_device.question_limit, "message": "You reached maximum chat question limit" }, status=status.HTTP_200_OK)


class DocChatView(APIView):

    def get_object(self, request, id):
        try:
            if request.user.is_superuser:
                return DocChatbot.objects.isActive().get(pk=id, user=request.user)
            return DocChatbot.objects.isActive().get(pk=id, is_demo=False)
        except DocChatbot.DoesNotExist:
            raise Http404

    def create_chat_history(self, chat):
        chat_prompt = [c['content'] for c in chat if c['role'] == 'user']
        chat_answer = [c['content'] for c in chat if c['role'] == 'assistant']
        return list(zip(chat_prompt, chat_answer))

    def conversational_chat(self, query, chatbot_id, chat_history):
        response = run_llm(query, f"faiss_index_{chatbot_id}", chat_history)
        return response['answer']

    def get(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        serializer = DocChatbotFetchSerializer(chatbot)
        chat = [{ "role": "assistant", "content": "Hi! 👋 What can I help you with?" }]
        chatbot_data = serializer.data
        os.environ["OPENAI_API_KEY"] = chatbot.open_ai_key if chatbot.open_ai_key else settings.OPENAI_API_KEY
        is_api_key_set = True if chatbot.open_ai_key else False
        chatbot_data['is_api_key_set'] = is_api_key_set
        return Response({ "chat": chat, "chatbot": chatbot_data, "is_api_key_set": is_api_key_set, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit }, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        serializer = DocChatbotSerializer(chatbot, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        chat = request.data['chat']
        last_chat = chat.pop()

        is_api_key_set = True if chatbot.open_ai_key else False
        os.environ["OPENAI_API_KEY"] = chatbot.open_ai_key if chatbot.open_ai_key else settings.OPENAI_API_KEY
        print(f"Used ENV KEY & is_api_key_set :: {os.environ['OPENAI_API_KEY']} :: {is_api_key_set}")

        chat_history = self.create_chat_history(chat[1:])
        print(chat_history)

        if is_api_key_set:
            print("Without Limit")
            chat_response = self.conversational_chat(last_chat['content'], chatbot.id, chat_history)
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": 0  }, status=status.HTTP_200_OK)
        elif chatbot.question_limit < settings.CHATBOT_QUESTION_LIMIT:
            print("With Limit")
            chat_response = self.conversational_chat(last_chat['content'], chatbot.id, chat_history)
            chatbot.question_limit += 1
            chatbot.save()
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit  }, status=status.HTTP_200_OK)
        return Response({ "message": "You reached maximum chat question limit" }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        chatbot.active = False
        chatbot.is_deleted = True
        chatbot.save()
        return Response({ "message": "chatbot deleted successfully" }, status=status.HTTP_200_OK)


class IframeChatStylesView(APIView):

    def get_object(self, request, id):
        try:
            return DocChatbot.objects.isActive().get(uuid=id, is_demo=False)
        except DocChatbot.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        chatbotId = request.GET.get('chatbotId', '')
        if not chatbotId:
            return Response({ "message": "chtbot id not correct, please add valid chatbot id" }, status=status.HTTP_400_BAD_REQUEST)
        chatbot = self.get_object(request, chatbotId)
        serializer = DocChatbotFetchSerializer(chatbot)
        chat = [{ "role": "assistant", "content": "Hi! 👋 What can I help you with?" }]
        chatbot_data = serializer.data
        os.environ["OPENAI_API_KEY"] = chatbot.open_ai_key if chatbot.open_ai_key else settings.OPENAI_API_KEY
        is_api_key_set = True if chatbot.open_ai_key else False
        chatbot_data['is_api_key_set'] = is_api_key_set
        return Response({
            "chat": chat,
            "domains": chatbot.domains,
            "is_api_key_set": is_api_key_set,
            "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit,
            "styles": {
                "align_chat_button": chatbot.align_chat_button,
                "auto_open_chat_window_after": chatbot.auto_open_chat_window_after,
                "button_color": chatbot.button_color,
                "chat_icon": chatbot.chat_icon if chatbot.chat_icon else "",
                "display_name": chatbot.display_name if chatbot.display_name else "",
                "theme": chatbot.theme,
                "user_message_color": chatbot.user_message_color
            },
            "initialMessages": chatbot.initial_messages.split('\n') if chatbot.initial_messages else ["Hi! 👋 What can I help you with?"]
        }, status=status.HTTP_200_OK)

class IframeDocChatView(APIView):

    def get_object(self, request, id):
        try:
            return DocChatbot.objects.isActive().get(uuid=id, is_demo=False)
        except DocChatbot.DoesNotExist:
            raise Http404
    
    def create_chat_history(self, chat):
        chat_prompt = [c['content'] for c in chat if c['role'] == 'user']
        chat_answer = [c['content'] for c in chat if c['role'] == 'assistant']
        return list(zip(chat_prompt, chat_answer))

    def conversational_chat(self, query, chatbot_id, chat_history):
        response = run_llm(query, f"faiss_index_{chatbot_id}", chat_history)
        return response['answer']

    def get(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        serializer = DocChatbotFetchSerializer(chatbot)
        chat = [{ "role": "assistant", "content": "Hi! 👋 What can I help you with?" }]
        chatbot_data = serializer.data
        os.environ["OPENAI_API_KEY"] = chatbot.open_ai_key if chatbot.open_ai_key else settings.OPENAI_API_KEY
        is_api_key_set = True if chatbot.open_ai_key else False
        chatbot_data['is_api_key_set'] = is_api_key_set
        return Response({
            "chat": chat,
            "is_api_key_set": is_api_key_set,
            "domains": chatbot.domains,
            "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit,
            "styles": {
                "align_chat_button": chatbot.align_chat_button,
                "auto_open_chat_window_after": chatbot.auto_open_chat_window_after,
                "button_color": chatbot.button_color,
                "chat_icon": chatbot.chat_icon if chatbot.chat_icon else "",
                "display_name": chatbot.display_name if chatbot.display_name else "",
                "theme": chatbot.theme,
                "user_message_color": chatbot.user_message_color,
                "logo": chatbot.bot_logo.url if chatbot.bot_logo else ""
            },
            "initialMessages": chatbot.initial_messages.split('\n') if chatbot.initial_messages else ["Hi! 👋 What can I help you with?"]
        }, status=status.HTTP_200_OK)
    
    def post(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        if chatbot.domains:
            if request.data['domain'] not in chatbot.domains.split('\n'):
                return Response({ "message": "Domain is not valid" }, status=status.HTTP_400_BAD_REQUEST)
        chat = request.data['chat']
        last_chat = chat.pop()

        is_api_key_set = True if chatbot.open_ai_key else False
        os.environ["OPENAI_API_KEY"] = chatbot.open_ai_key if chatbot.open_ai_key else settings.OPENAI_API_KEY

        print(f"Used ENV KEY & is_api_key_set :: {os.environ['OPENAI_API_KEY']} :: {is_api_key_set}")

        chat_history = self.create_chat_history(chat[1:])
        print(chat_history)

        if is_api_key_set:
            print("Without Limit")
            chat_response = self.conversational_chat(last_chat['content'], chatbot.id, chat_history)
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": 0  }, status=status.HTTP_200_OK)
        elif chatbot.question_limit < settings.CHATBOT_QUESTION_LIMIT:
            print("With Limit")
            chat_response = self.conversational_chat(last_chat['content'], chatbot.id, chat_history)
            chatbot.question_limit += 1
            chatbot.save()
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit  }, status=status.HTTP_200_OK)
        return Response({ "message": "You reached maximum chat question limit" }, status=status.HTTP_400_BAD_REQUEST)
