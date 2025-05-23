# Generated by Django 5.1.6 on 2025-02-25 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='summary',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='book',
            name='cover',
        ),
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='books/covers/'),
        ),
        migrations.AddField(
            model_name='book',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('reserved', 'Reserved'), ('borrowed', 'Borrowed')], default='available', max_length=20),
        ),
    ]
