from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.translation import gettext_lazy as _
from geeks_ai_backend.models import ActivityTracking
from geeks_ai_backend.managers import ActivityQuerySet
from chatbot.aws import S3

class ChatbotFile(ActivityTracking):
    name = models.CharField(max_length=255,
                help_text=_('File name'), 
                verbose_name=_('File name'))
    url = models.TextField(blank=True, null=True,
                help_text=_('File URL'),
                verbose_name=_('File URL'))

    def __str__(self):
            return self.name

    class Meta:
        verbose_name = _("Chatbot File")
        verbose_name_plural = _("Chatbot Files")
        ordering = ['-created_at']

class Chatbot(ActivityTracking):
    CHATBOT_CATEGORIES = (
        ('1', _('Text')),
        ('2', _('CSV')),
    )

    CHATBOT_MODEL = (
        ('1', _('gpt-3.5-turbo')),
    )

    user = models.ForeignKey('authentication.Account',
                related_name='user',
                on_delete=models.CASCADE)
    name = models.CharField(max_length=128,
                help_text=_('Chatbot name'), 
                verbose_name=_('Chatbot name'))
    description = models.TextField(blank=True, null=True, 
                help_text=_('Chatbot Description'),
                verbose_name=_('Chatbot Description'))
    file_urls = models.ManyToManyField('chatbot.ChatbotFile', blank=True,
                related_name='chatbot_file_urls',
                help_text=_('Chatbot file urls'),
                verbose_name=_('Chatbot file urls'))
    category = models.CharField(max_length=11,
                choices=CHATBOT_CATEGORIES,
                help_text=_('Chatbot category'),
                verbose_name=_('Chatbot category'),
                default='1')
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
    
    objects = ActivityQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Chatbot")
        verbose_name_plural = _("Chatbots")
        ordering = ['-created_at']