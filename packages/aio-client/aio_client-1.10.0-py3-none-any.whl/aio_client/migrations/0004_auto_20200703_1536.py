# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0003_auto_20190201_0530'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='getconsumerreceipt',
            options={'verbose_name': 'Потребитель. Ответ СМЭВ по заявкам'},
        ),
        migrations.AlterModelOptions(
            name='getconsumerresponse',
            options={'verbose_name': 'Потребитель. Ответ СМЭВ'},
        ),
        migrations.AlterModelOptions(
            name='getproviderreceipt',
            options={'verbose_name': 'Поставщик. Ответ СМЭВ по заявкам'},
        ),
        migrations.AlterModelOptions(
            name='getproviderrequest',
            options={'verbose_name': 'Поставщик. Заявки от СМЭВ'},
        ),
        migrations.AlterModelOptions(
            name='postconsumerrequest',
            options={'verbose_name': 'Потребитель. Заявки в СМЭВ'},
        ),
        migrations.AlterModelOptions(
            name='postproviderrequest',
            options={'verbose_name': 'Поставщик. Ответ на заявку'},
        ),
        migrations.AlterModelOptions(
            name='requestlog',
            options={
                'verbose_name': 'HTTP запрос',
                'verbose_name_plural': 'HTTP запросы'
            },
        ),
        migrations.AlterField(
            model_name='getconsumerreceipt',
            name='error',
            field=models.TextField(
                default='',
                verbose_name=
                'Сообщение об ошибке, возникшей при передаче данных в СМЭВ'),
        ),
        migrations.AlterField(
            model_name='getproviderreceipt',
            name='error',
            field=models.TextField(
                default='',
                verbose_name=
                'Сообщение об ошибке, возникшей при передаче данных в СМЭВ'),
        ),
        migrations.AlterField(
            model_name='postproviderrequest',
            name='content_failure_code',
            field=models.CharField(blank=True,
                                   choices=[('ACCESS_DENIED', 'access denied'),
                                            ('UNKNOWN_REQUEST_DESCRIPTION',
                                             'unknown request description'),
                                            ('NO_DATA', 'no data'),
                                            ('FAILURE', 'failure')],
                                   max_length=50,
                                   null=True,
                                   verbose_name='Код причины отказа'),
        ),
        migrations.AlterField(
            model_name='postproviderrequest',
            name='content_failure_comment',
            field=models.TextField(blank=True,
                                   default='',
                                   verbose_name='Пояснение причины отказа'),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='error',
            field=models.TextField(default='',
                                   verbose_name='Текст ошибки запроса'),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='http_header',
            field=models.TextField(
                default='{"Content-Type": "application/json;charset=utf-8"}',
                verbose_name='Заголовок http запроса'),
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
        migrations.AlterField(
            model_name='requestlog',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
    ]
