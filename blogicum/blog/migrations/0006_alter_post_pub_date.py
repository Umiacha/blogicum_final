# Generated by Django 3.2.16 on 2023-06-23 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(blank=True, help_text='Если установить дату и время в будущем — можно делать отложенные публикации.', null=True, verbose_name='Дата и время публикации'),
        ),
    ]
