# Generated by Django 4.2.7 on 2023-11-16 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_customuser_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='first_aid_response',
            field=models.TextField(blank=True, null=True),
        ),
    ]
