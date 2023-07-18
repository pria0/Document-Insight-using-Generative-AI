from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.translation import gettext_lazy as _
from csvgpt.models import ActivityTracking
from csvgpt.managers import ActivityQuerySet
from chatbot.aws import S3

class DocChatbotFile(ActivityTracking):
    name = models.CharField(max_length=255,
                help_text=_('File name'), 
                verbose_name=_('File name'))
    url = models.TextField(blank=True, null=True,
                help_text=_('File URL'),
                verbose_name=_('File URL'))
    num_of_characters = models.IntegerField(help_text=_('Number of characters'), 
                verbose_name=_('Number of characters'),
                default=0)

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = _("Doc Chatbot File")
        verbose_name_plural = _("Doc Chatbot Files")
        ordering = ['-created_at']


class DocChatbot(ActivityTracking):

    CHATBOT_MODEL = (
        ('1', _('gpt-3.5-turbo')),
    )

    ALIGN_CHAT_BUTTON = (
        ('left', _('Left')),
        ('right', _('Right')),
    )

    BOT_THEME = (
        ('light', _('Light')),
        ('dark', _('Dark')),
    )

    user = models.ForeignKey('authentication.Account',
                related_name='doc_gpt_user',
                on_delete=models.CASCADE)
    name = models.CharField(max_length=128,
                help_text=_('Chatbot name'), 
                verbose_name=_('Chatbot name'))
    description = models.TextField(blank=True, null=True, 
                help_text=_('Chatbot Description'),
                verbose_name=_('Chatbot Description'))
    file_urls = models.ManyToManyField('docgpt.DocChatbotFile', blank=True,
                related_name='chatbot_file_urls',
                help_text=_('Chatbot file urls'),
                verbose_name=_('Chatbot file urls'))
    bot_logo = models.ForeignKey('docgpt.DocChatbotFile', blank=True,
                related_name='chatbot_logo_url',
                help_text=_('Chatbot logo url'),
                verbose_name=_('Chatbot logo url'),
                null=True,
                on_delete=models.SET_NULL)
    base_prompt = models.TextField(blank=True, null=True,
                help_text=_('Chatbot base prompt'),
                verbose_name=_('Chatbot base prompt'))
    model = models.CharField(max_length=11,
                choices=CHATBOT_MODEL,
                help_text=_('Chatbot model'),
                verbose_name=_('Chatbot model'),
                default='1')
    question_limit = models.IntegerField(help_text=_('Question limit'), 
                verbose_name=_('Question limit'),
                default=0)
    open_ai_key = models.CharField(max_length=255,
                blank=True, null=True,
                help_text=_('Open ai key'), 
                verbose_name=_('Open ai key'), default="")
    is_demo = models.BooleanField(verbose_name=_('Is Demo'), default=False)
    initial_messages = models.TextField(blank=True, null=True,
                help_text=_('Chatbot initial messages'),
                verbose_name=_('Chatbot initial messages'),
                default="Hi! 👋 What can I help you with?")
    align_chat_button = models.CharField(max_length=11,
                choices=ALIGN_CHAT_BUTTON,
                help_text=_('Align chat button'),
                verbose_name=_('Align chat button'),
                default='right')
    auto_open_chat_window_after = models.IntegerField(help_text=_('Auto open chat window after'), 
                verbose_name=_('Auto open chat window after'),
                default=2)
    button_color = models.CharField(max_length=28,
                blank=True, null=True,
                help_text=_('Chat button color'),
                verbose_name=_('Chat button color'),
                default='#000000')
    display_name = models.CharField(max_length=128,
                blank=True, null=True,
                help_text=_('Display bot name'),
                verbose_name=_('Display bot name'),
                default='')
    theme = models.CharField(max_length=11,
                choices=BOT_THEME,
                help_text=_('Bot theme'),
                verbose_name=_('Bot theme'),
                default='light')
    user_message_color = models.CharField(max_length=28,
                blank=True, null=True,
                help_text=_('User message color'),
                verbose_name=_('User message color'),
                default='#3B81F6')
    chat_icon = models.ForeignKey('docgpt.DocChatbotFile', blank=True,
                related_name='chat_icon_url',
                help_text=_('Chat icon url'),
                verbose_name=_('Chat icon url'),
                null=True,
                on_delete=models.SET_NULL)
    domains = models.TextField(blank=True, null=True,
                help_text=_('Chatbot allowed domains'),
                verbose_name=_('Chatbot allowed domains'))
    base_prompt_message = models.TextField(blank=True, null=True,
                help_text=_('Chatbot base prompt message'),
                verbose_name=_('Chatbot base prompt message'))
    second_base_prompt_message = models.TextField(blank=True, null=True,
                help_text=_('Chatbot second base prompt message'),
                verbose_name=_('Chatbot second base prompt message'))
    
    objects = ActivityQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Doc Chatbot")
        verbose_name_plural = _("Doc Chatbots")
        ordering = ['-created_at']


class DocChatbotDevice(ActivityTracking):
    fingerprint = models.CharField(max_length=255,
                help_text=_('Device Fingerprint'), 
                verbose_name=_('Device Fingerprint'))
    question_limit = models.IntegerField(help_text=_('Question limit'), 
                verbose_name=_('Question limit'),
                default=0)
    chatbot = models.ForeignKey('docgpt.DocChatbot',
                related_name='chatbot',
                null=True,
                on_delete=models.SET_NULL)

    def __str__(self):
            return self.fingerprint

    class Meta:
        verbose_name = _("Doc chatbot devices")
        verbose_name_plural = _("Doc chatbot devices")
        ordering = ['-created_at']