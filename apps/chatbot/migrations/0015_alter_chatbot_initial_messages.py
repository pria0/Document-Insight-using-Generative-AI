# Generated by Django 4.2.1 on 2023-05-25 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0014_chatbot_initial_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatbot',
            name='initial_messages',
            field=models.TextField(blank=True, default='Hi! 👋 What can I help you with?', help_text='Chatbot initial messages', null=True, verbose_name='Chatbot initial messages'),
        ),
    ]
