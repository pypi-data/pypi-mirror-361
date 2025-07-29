# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [('aio_client', '0001_initial'), ]

    operations = [
        migrations.AlterModelOptions(
            name='getconsumerreceipt',
            options={'verbose_name': 'Поставщик. Ответ СМЭВ по заявкам'}, ),
        migrations.AlterModelOptions(
            name='getconsumerresponse',
            options={'verbose_name': 'Поставщик. Ответ СМЭВ'}, ),
        migrations.AlterModelOptions(
            name='getproviderreceipt',
            options={'verbose_name': 'Провайдер. Ответ СМЭВ по заявкам'}, ),
        migrations.AlterModelOptions(
            name='getproviderrequest',
            options={'verbose_name': 'Провайдер. Заявки от СМЭВ'}, ),
        migrations.AlterModelOptions(
            name='postconsumerrequest',
            options={'verbose_name': 'Поставщик. Заявки в СМЭВ'}, ),
        migrations.AlterModelOptions(
            name='postproviderrequest',
            options={'verbose_name': 'Провайдер. Ответ на заявку'}, ),
        migrations.AlterModelOptions(
            name='requestlog',
            options={'verbose_name': 'HTTP запросы'}, ),
        migrations.AlterField(
            model_name='getconsumerreceipt',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен'), (2, 'Отправлен'), (3, 'Ошибка')],
                default=1,
                verbose_name='Состояние пакетов'), ),
        migrations.AlterField(
            model_name='getconsumerresponse',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен'), (2, 'Отправлен'), (3, 'Ошибка')],
                default=1,
                verbose_name='Состояние пакетов'), ),
        migrations.AlterField(
            model_name='getproviderreceipt',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен'), (2, 'Отправлен'), (3, 'Ошибка')],
                default=1,
                verbose_name='Состояние пакетов'), ),
        migrations.AlterField(
            model_name='getproviderrequest',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен в РИС'), (2, 'Отправлен в РИС'), (
                    3, 'Ошибка')],
                default=1,
                verbose_name='Состояние пакетов'), ),
        migrations.AlterField(
            model_name='postconsumerrequest',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен'), (2, 'Отправлен'), (3, 'Ошибка')],
                default=1,
                verbose_name='Состояние пакетов'), ),
        migrations.AlterField(
            model_name='postproviderrequest',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен'), (2, 'Отправлен'), (3, 'Ошибка')],
                default=1,
                verbose_name='Состояние пакетов'), ),
        migrations.AlterField(
            model_name='requestlog',
            name='error',
            field=models.TextField(
                default=b'', verbose_name='Текст ошибки запроса'), ),
        migrations.AlterField(
            model_name='requestlog',
            name='request_type',
            field=models.CharField(
                choices=[
                    (b'delete/api/v0/as-provider/receipt/',
                     'Поставщик.Запрос на удаление полученных ответов от СМЭВ'
                     ), (b'post/api/v0/as-consumer/request/',
                         'Потребитель.Передача заявок в СМЭВ'),
                    (b'delete/api/v0/as-consumer/response/',
                     'Потребитель.Запрос на удаление полученных ответов'),
                    (b'post/api/v0/as-provider/response/',
                     'Поставщик.Передача ответа на заявки'),
                    (b'delete/api/v0/as-provider/request/',
                     'Поставщик.Запрос на удаление полученных заявок'),
                    (b'get/api/v0/as-provider/receipt',
                     'Поставщик.Получение ответа СМЭВ по всем отправленным заявкам'
                     ), (b'get/api/v0/as-consumer/response/',
                         'Потребитель.Получение всех ответов из очереди СМЭВ'),
                    (b'delete/api/v0/as-consumer/receipt/',
                     'Потребитель.Запрос на удаление полученных ответов от СМЭВ'
                     ), (b'get/api/v0/as-provider/request',
                         'Поставщик.Получение всех заявок к РИС'),
                    (b'get/api/v0/as-consumer/receipt',
                     'Потребитель.Получение ответа СМЭВ по всем отправленным заявкам'
                     )
                ],
                default=b'get/api/v0/as-provider/request',
                max_length=100,
                verbose_name='Тип запроса'), ),
        migrations.AlterField(
            model_name='requestlog',
            name='state',
            field=models.SmallIntegerField(
                choices=[(1, 'Не отправлен'), (2, 'Отправлен'), (3, 'Ошибка')],
                default=1,
                verbose_name='Статус запроса'), ),
    ]
