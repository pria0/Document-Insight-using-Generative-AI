# Generated by Django 4.2.1 on 2023-06-01 11:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DocChatbot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is Deleted')),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=36, verbose_name='Uuid')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date when created.', null=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date when updated.', null=True, verbose_name='Updated At')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, help_text='Date when deleted', null=True, verbose_name='Deleted At')),
                ('delete_reason', models.CharField(blank=True, default=None, help_text='Delete Reason', max_length=300, null=True, verbose_name='Delete Reason')),
                ('name', models.CharField(help_text='Chatbot name', max_length=128, verbose_name='Chatbot name')),
                ('description', models.TextField(blank=True, help_text='Chatbot Description', null=True, verbose_name='Chatbot Description')),
                ('base_prompt', models.TextField(blank=True, help_text='Chatbot base prompt', null=True, verbose_name='Chatbot base prompt')),
                ('model', models.CharField(choices=[('1', 'gpt-3.5-turbo')], default='1', help_text='Chatbot model', max_length=11, verbose_name='Chatbot model')),
                ('question_limit', models.IntegerField(default=0, help_text='Question limit', verbose_name='Question limit')),
                ('open_ai_key', models.CharField(blank=True, default='', help_text='Open ai key', max_length=255, null=True, verbose_name='Open ai key')),
                ('is_demo', models.BooleanField(default=False, verbose_name='Is Demo')),
                ('initial_messages', models.TextField(blank=True, default='Hi! 👋 What can I help you with?', help_text='Chatbot initial messages', null=True, verbose_name='Chatbot initial messages')),
                ('align_chat_button', models.CharField(choices=[('left', 'Left'), ('right', 'Right')], default='right', help_text='Align chat button', max_length=11, verbose_name='Align chat button')),
                ('auto_open_chat_window_after', models.IntegerField(default=2, help_text='Auto open chat window after', verbose_name='Auto open chat window after')),
                ('button_color', models.CharField(blank=True, default='#000000', help_text='Chat button color', max_length=28, null=True, verbose_name='Chat button color')),
                ('display_name', models.CharField(blank=True, default='', help_text='Display bot name', max_length=128, null=True, verbose_name='Display bot name')),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', help_text='Bot theme', max_length=11, verbose_name='Bot theme')),
                ('user_message_color', models.CharField(blank=True, default='#3B81F6', help_text='User message color', max_length=28, null=True, verbose_name='User message color')),
                ('domains', models.TextField(blank=True, help_text='Chatbot allowed domains', null=True, verbose_name='Chatbot allowed domains')),
            ],
            options={
                'verbose_name': 'Doc Chatbot',
                'verbose_name_plural': 'Doc Chatbots',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DocChatbotFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is Deleted')),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=36, verbose_name='Uuid')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date when created.', null=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date when updated.', null=True, verbose_name='Updated At')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, help_text='Date when deleted', null=True, verbose_name='Deleted At')),
                ('delete_reason', models.CharField(blank=True, default=None, help_text='Delete Reason', max_length=300, null=True, verbose_name='Delete Reason')),
                ('name', models.CharField(help_text='File name', max_length=255, verbose_name='File name')),
                ('url', models.TextField(blank=True, help_text='File URL', null=True, verbose_name='File URL')),
            ],
            options={
                'verbose_name': 'Doc Chatbot File',
                'verbose_name_plural': 'Doc Chatbot Files',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DocChatbotDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is Deleted')),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=36, verbose_name='Uuid')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date when created.', null=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date when updated.', null=True, verbose_name='Updated At')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, help_text='Date when deleted', null=True, verbose_name='Deleted At')),
                ('delete_reason', models.CharField(blank=True, default=None, help_text='Delete Reason', max_length=300, null=True, verbose_name='Delete Reason')),
                ('fingerprint', models.CharField(help_text='Device Fingerprint', max_length=255, verbose_name='Device Fingerprint')),
                ('question_limit', models.IntegerField(default=0, help_text='Question limit', verbose_name='Question limit')),
                ('chatbot', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chatbot', to='docgpt.docchatbot')),
            ],
            options={
                'verbose_name': 'Doc chatbot devices',
                'verbose_name_plural': 'Doc chatbot devices',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='docchatbot',
            name='bot_logo',
            field=models.ForeignKey(blank=True, help_text='Chatbot logo url', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chatbot_logo_url', to='docgpt.docchatbotfile', verbose_name='Chatbot logo url'),
        ),
        migrations.AddField(
            model_name='docchatbot',
            name='chat_icon',
            field=models.ForeignKey(blank=True, help_text='Chat icon url', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_icon_url', to='docgpt.docchatbotfile', verbose_name='Chat icon url'),
        ),
        migrations.AddField(
            model_name='docchatbot',
            name='file_urls',
            field=models.ManyToManyField(blank=True, help_text='Chatbot file urls', related_name='chatbot_file_urls', to='docgpt.docchatbotfile', verbose_name='Chatbot file urls'),
        ),
        migrations.AddField(
            model_name='docchatbot',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doc_gpt_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
