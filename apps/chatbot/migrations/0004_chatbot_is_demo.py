# Generated by Django 4.2.1 on 2023-05-22 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_chatbot_open_ai_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatbot',
            name='is_demo',
            field=models.BooleanField(default=False, verbose_name='Is Demo'),
        ),
    ]
