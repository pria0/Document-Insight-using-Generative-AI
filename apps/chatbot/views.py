import os
from django.conf import settings
from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from chatbot.models import Chatbot, ChatbotDevice, ChatbotFile
from chatbot.serializers import ChatbotFileSerializer, ChatbotSerializer, ChatbotFetchSerializer

from langchain.agents import create_csv_agent
from langchain.chat_models import ChatOpenAI
# Create your views here.

class ChatbotFileView(APIView):

    def post(self, request):
        requestFile = request.FILES.get('uploadFile')
        serializer = ChatbotFileSerializer(data={ 'name': requestFile.name, 'file': requestFile })
        if serializer.is_valid():
            obj = serializer.save()
            obj.url = obj.file.url
            obj.save()
            return Response({ 'sUrl': obj.file.url, 'fileId': obj.id, 'pUrl': obj.file.url }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatbotView(APIView):

    def get(self, request, format=None):
        if request.user.is_superuser:
            chatbots = Chatbot.objects.isActive().filter(user=request.user)
        else:
            chatbots = Chatbot.objects.isActive().filter(is_demo=False)
        serializer = ChatbotFetchSerializer(chatbots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = ChatbotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatbotDemoView(APIView):
    def post(self, request, format=None):
        fingerprint = request.data['fingerprint'] if 'fingerprint' in request.data.keys() else ''
        chatbots = Chatbot.objects.isActive().filter(is_demo=True)
        serializer = ChatbotFetchSerializer(chatbots, many=True)
        for chatbot in chatbots:
            obj, created = ChatbotDevice.objects.update_or_create(fingerprint=fingerprint, chatbot=chatbot)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DemoChatView(APIView):

    def get_object(self, request, id):
        try:
            return Chatbot.objects.isActive().get(pk=id, is_demo=True)
        except Chatbot.DoesNotExist:
            raise Http404

    def conversational_chat(self, query, uploaded_file):
        print(uploaded_file.replace(' ', '%20'))
        csv_agent = create_csv_agent(ChatOpenAI(temperature=0, model_name="gpt-4"), uploaded_file.replace(' ', '%20'), verbose=False)
        try:
            response= csv_agent.run(query)
        except Exception as e:
            response = str(e)
            if response.startswith("Could not parse LLM output: `"):
                response = response.removeprefix("Could not parse LLM output: `").removesuffix("`")
        return response

    def get(self, request, id, format=None):
        fingerprint = request.GET.get('fingerprint', '')
        isHomePage = request.GET.get('isHomePage', '') == 'true'
        chatbot = self.get_object(request, id)
        if isHomePage and not ChatbotDevice.objects.filter(fingerprint=fingerprint, chatbot__id=id).exists():
            obj, created = ChatbotDevice.objects.update_or_create(fingerprint=fingerprint, chatbot=chatbot)
        elif not ChatbotDevice.objects.filter(fingerprint=fingerprint, chatbot__id=id).exists():
            return Response({ "status": status.HTTP_400_BAD_REQUEST, "message": "Device fingerprint not matched" }, status=status.HTTP_200_OK)

        serializer = ChatbotFetchSerializer(chatbot)
        chat = [{ "role": "assistant", "content": "Hi! 👋 What can I help you with?" }]
        chatbot_data = serializer.data

        chatbot_device = ChatbotDevice.objects.get(fingerprint=fingerprint, chatbot__id=id)

        return Response({ "chat": chat, "chatbot": chatbot_data, "is_api_key_set": False, "question_limit": settings.DEMO_CHATBOT_QUESTION_LIMIT - chatbot_device.question_limit }, status=status.HTTP_200_OK)
    
    def post(self, request, id, format=None):
        fingerprint = request.data['fingerprint'] if 'fingerprint' in request.data.keys() else ''
        if not ChatbotDevice.objects.filter(fingerprint=fingerprint, chatbot__id=id).exists():
            return Response({ "status": status.HTTP_400_BAD_REQUEST, "message": "Device fingerprint not matched" }, status=status.HTTP_200_OK)
        chatbot = self.get_object(request, id)
        chat = request.data['chat']
        last_chat = chat.pop()

        chatbot_device = ChatbotDevice.objects.get(fingerprint=fingerprint, chatbot__id=id)
        if chatbot_device.question_limit < settings.DEMO_CHATBOT_QUESTION_LIMIT:
            chat_response = self.conversational_chat(last_chat['content'], f"{settings.LOCAL_HOST_PORT}{chatbot.file_urls.all()[0].url}")
            chatbot_device.question_limit += 1
            chatbot_device.save()
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": False, "question_limit": settings.DEMO_CHATBOT_QUESTION_LIMIT - chatbot_device.question_limit  }, status=status.HTTP_200_OK)
        return Response({ "status": status.HTTP_400_BAD_REQUEST, "question_limit": settings.DEMO_CHATBOT_QUESTION_LIMIT - chatbot_device.question_limit, "message": "You reached maximum chat question limit" }, status=status.HTTP_200_OK)


class ChatView(APIView):

    def get_object(self, request, id):
        try:
            if request.user.is_superuser:
                return Chatbot.objects.isActive().get(pk=id, user=request.user)
            return Chatbot.objects.isActive().get(pk=id, is_demo=False)
        except Chatbot.DoesNotExist:
            raise Http404

    def conversational_chat(self, query, uploaded_file):
        csv_agent = create_csv_agent(ChatOpenAI(temperature=0, model_name="gpt-4"), uploaded_file.replace(' ', '%20'), verbose=False)
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
        chat = [{ "role": "assistant", "content": "Hi! 👋 What can I help you with?" }]
        chatbot_data = serializer.data
        os.environ["OPENAI_API_KEY"] = chatbot.open_ai_key if chatbot.open_ai_key else settings.OPENAI_API_KEY
        is_api_key_set = True if chatbot.open_ai_key else False
        chatbot_data['is_api_key_set'] = is_api_key_set
        return Response({ "chat": chat, "chatbot": chatbot_data, "is_api_key_set": is_api_key_set, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit }, status=status.HTTP_200_OK)

    def put(self, request, id, format=None):
        chatbot = self.get_object(request, id)
        serializer = ChatbotSerializer(chatbot, data=request.data, partial=True)
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

        # chat_history = ", ".join([ c['content'] for c in chat[1:] if c['role'] == 'user' ])
        # PROMPT = f"""
        #     Take this list of chat history separated by comma {chat_history} as context.
        #     Question: {last_chat['content']} and give answer based on context.
        #     if list is not provided or not relevant to context then give answer based on question only.
        #     Give answer of question only.
        # """
        # print(PROMPT)
        print(f"Used ENV KEY & is_api_key_set :: {os.environ['OPENAI_API_KEY']} :: {is_api_key_set}")
        if is_api_key_set:
            print("Without Limit")
            chat_response = self.conversational_chat(last_chat['content'], f"{settings.LOCAL_HOST_PORT}{chatbot.file_urls.all()[0].url}")
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": 0  }, status=status.HTTP_200_OK)
        elif chatbot.question_limit < settings.CHATBOT_QUESTION_LIMIT:
            print("With Limit")
            chat_response = self.conversational_chat(last_chat['content'], f"{settings.LOCAL_HOST_PORT}{chatbot.file_urls.all()[0].url}")
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
            return Chatbot.objects.isActive().get(uuid=id, is_demo=False)
        except Chatbot.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        chatbotId = request.GET.get('chatbotId', '')
        if not chatbotId:
            return Response({ "message": "chtbot id not correct, please add valid chatbot id" }, status=status.HTTP_400_BAD_REQUEST)
        chatbot = self.get_object(request, chatbotId)
        serializer = ChatbotFetchSerializer(chatbot)
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

class IframeChatView(APIView):

    def get_object(self, request, id):
        try:
            return Chatbot.objects.isActive().get(uuid=id, is_demo=False)
        except Chatbot.DoesNotExist:
            raise Http404

    def conversational_chat(self, query, uploaded_file):
        csv_agent = create_csv_agent(ChatOpenAI(temperature=0, model_name="gpt-4"), uploaded_file.replace(' ', '%20'), verbose=False)
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
                "user_message_color": chatbot.user_message_color
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
        if is_api_key_set:
            print("Without Limit")
            chat_response = self.conversational_chat(last_chat['content'], f"{settings.LOCAL_HOST_PORT}{chatbot.file_urls.all()[0].url}")
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": 0  }, status=status.HTTP_200_OK)
        elif chatbot.question_limit < settings.CHATBOT_QUESTION_LIMIT:
            print("With Limit")
            chat_response = self.conversational_chat(last_chat['content'], f"{settings.LOCAL_HOST_PORT}{chatbot.file_urls.all()[0].url}")
            chatbot.question_limit += 1
            chatbot.save()
            return Response({ "chat" : { "role": "assistant", "content": chat_response }, "is_api_key_set": is_api_key_set, "question_limit": settings.CHATBOT_QUESTION_LIMIT - chatbot.question_limit  }, status=status.HTTP_200_OK)
        return Response({ "message": "You reached maximum chat question limit" }, status=status.HTTP_400_BAD_REQUEST)
