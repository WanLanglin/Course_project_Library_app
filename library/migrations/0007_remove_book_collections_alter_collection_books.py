# Generated by Django 5.1.6 on 2025-03-28 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_book_collections_alter_collection_books'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='collections',
        ),
        migrations.AlterField(
            model_name='collection',
            name='books',
            field=models.ManyToManyField(blank=True, related_name='collections', to='library.book'),
        ),
    ]
