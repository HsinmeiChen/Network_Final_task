# Generated by Django 5.1.2 on 2024-12-18 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_teachingsession_guide_index_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teachingsession',
            name='current_state',
            field=models.CharField(default='Idle', max_length=50),
        ),
    ]
