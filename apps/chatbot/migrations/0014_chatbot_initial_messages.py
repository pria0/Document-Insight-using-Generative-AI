# Generated by Django 4.2.1 on 2023-05-24 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0013_chatbot_domains'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbot',
            name='initial_messages',
            field=models.TextField(blank=True, help_text='Chatbot initial messages', null=True, verbose_name='Chatbot initial messages'),
        ),
    ]