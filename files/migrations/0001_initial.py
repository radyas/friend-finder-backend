# Generated by Django 4.0.3 on 2022-03-19 06:50

from django.db import migrations, models
import files.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to=files.models.file_path)),
                ('file_name', models.TextField()),
            ],
        ),
    ]