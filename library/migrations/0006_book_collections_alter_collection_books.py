# Generated by Django 5.1.6 on 2025-03-27 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_alter_collection_books'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='collections',
            field=models.ManyToManyField(blank=True, related_name='book_set', to='library.collection'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='books',
            field=models.ManyToManyField(blank=True, related_name='collection_set', to='library.book'),
        ),
    ]
