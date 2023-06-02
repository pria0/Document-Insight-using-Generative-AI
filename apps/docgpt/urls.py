from django.urls import path
from docgpt.views import DocgptbotView, DocgptFileView, DocChatView, DocgptbotDemoView, DemoDocChatView, IframeDocChatView, IframeChatStylesView


app_name = 'docgpt'
urlpatterns = [
    path('', DocgptbotView.as_view(), name="doc_chat_bot"),
    path('demo/', DocgptbotDemoView.as_view(), name="demo_doc_bot_chat"),
    path('signedurl/', DocgptFileView.as_view(), name="doc_file_signed_url"),
    path('iframe-styles/', IframeChatStylesView.as_view(), name="iframe_style_doc_bot_chat"),
    path('<int:id>/chat/', DocChatView.as_view(), name="doc_bot_chat"),
    path('<int:id>/demo/chat/', DemoDocChatView.as_view(), name="demo_doc_bot_chat"),
    path('<str:id>/iframe/chat/', IframeDocChatView.as_view(), name="iframe_doc_bot_chat"),
]