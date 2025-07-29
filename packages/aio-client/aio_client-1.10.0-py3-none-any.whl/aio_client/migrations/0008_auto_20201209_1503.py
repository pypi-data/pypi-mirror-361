# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0007_auto_20201113_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestlog',
            name='error_http_body',
            field=models.TextField(
                default='',
                verbose_name='Тело http ответа при возникновении ошибки'),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='request_type',
            field=models.CharField(choices=[
                ('get/api/v0/as-provider/request',
                 'Поставщик.Получение всех заявок к РИС'),
                ('delete/api/v0/as-provider/request/',
                 'Поставщик.Запрос на удаление полученных заявок'),
                ('post/api/v0/as-provider/response/',
                 'Поставщик.Передача ответа на заявки'),
                ('get/api/v0/as-provider/receipt',
                 'Поставщик.Получение ответа СМЭВ по всем отправленным заявкам'
                 ),
                ('delete/api/v0/as-provider/receipt/',
                 'Поставщик.Запрос на удаление полученных ответов от СМЭВ'),
                ('post/api/v0/as-consumer/request/',
                 'Потребитель.Передача заявок в СМЭВ'),
                ('get/api/v0/as-consumer/receipt',
                 'Потребитель.Получение ответа СМЭВ по всем отправленным заявкам'
                 ),
                ('delete/api/v0/as-consumer/receipt/',
                 'Потребитель.Запрос на удаление полученных ответов от СМЭВ'),
                ('get/api/v0/as-consumer/response/',
                 'Потребитель.Получение всех ответов из очереди СМЭВ'),
                ('delete/api/v0/as-consumer/response/',
                 'Потребитель.Запрос на удаление полученных ответов')
            ],
                                   default='get/api/v0/as-provider/request',
                                   max_length=100,
                                   verbose_name='Тип запроса'),
        ),
    ]
