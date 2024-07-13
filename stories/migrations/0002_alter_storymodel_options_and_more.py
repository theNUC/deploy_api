# Generated by Django 5.0.6 on 2024-07-13 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='storymodel',
            options={'ordering': ('-expire_time',), 'verbose_name': 'Story', 'verbose_name_plural': 'Stories'},
        ),
        migrations.RenameField(
            model_name='storymodel',
            old_name='expiry_time',
            new_name='expire_time',
        ),
        migrations.AlterField(
            model_name='storymodel',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]