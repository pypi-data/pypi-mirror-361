# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations
from django.db import models
import django.contrib.postgres.fields.jsonb
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='GetConsumerReceipt',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('message_type', models.CharField(
                    max_length=100, verbose_name='Вид сведений')),
                ('message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор сообщения')),
                ('origin_message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО'
                )),
                ('error', models.TextField(
                    default=b'',
                    verbose_name='Сообщение об ошибке, возникшей при передаче данных в СМЭВ'
                )),
                ('fault', models.BooleanField(
                    default=False,
                    verbose_name='Признак успешного взаимодействия')),
            ],
            options={'abstract': False, }, ),
        migrations.CreateModel(
            name='GetConsumerResponse',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('message_type', models.CharField(
                    max_length=100, verbose_name='Вид сведений')),
                ('message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор сообщения')),
                ('origin_message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО'
                )),
                ('body', models.TextField(
                    verbose_name='Бизнес-данные запроса')),
                ('attachments', django.contrib.postgres.fields.jsonb.JSONField(
                    blank=True, null=True, verbose_name='Вложения запроса')),
            ],
            options={'abstract': False, }, ),
        migrations.CreateModel(
            name='GetProviderReceipt',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('message_type', models.CharField(
                    max_length=100, verbose_name='Вид сведений')),
                ('message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор сообщения')),
                ('origin_message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО'
                )),
                ('error', models.TextField(
                    default=b'',
                    verbose_name='Сообщение об ошибке, возникшей при передаче данных в СМЭВ'
                )),
                ('fault', models.BooleanField(
                    default=False,
                    verbose_name='Признак успешного взаимодействия')),
            ],
            options={'abstract': False, }, ),
        migrations.CreateModel(
            name='GetProviderRequest',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('message_type', models.CharField(
                    max_length=100, verbose_name='Вид сведений')),
                ('message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор сообщения')),
                ('origin_message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО'
                )),
                ('body', models.TextField(
                    verbose_name='Бизнес-данные запроса')),
                ('attachments', django.contrib.postgres.fields.jsonb.JSONField(
                    blank=True, null=True, verbose_name='Вложения запроса')),
                ('is_test_message', models.BooleanField(
                    default=False,
                    verbose_name='Признак тестового взаимодействия')),
                ('replay_to', models.CharField(
                    max_length=100, verbose_name='Индекс сообщения в СМЭВ')),
            ],
            options={'abstract': False, }, ),
        migrations.CreateModel(
            name='PostConsumerRequest',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('message_type', models.CharField(
                    max_length=100, verbose_name='Вид сведений')),
                ('message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор сообщения')),
                ('origin_message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО'
                )),
                ('body', models.TextField(
                    verbose_name='Бизнес-данные запроса')),
                ('attachments', django.contrib.postgres.fields.jsonb.JSONField(
                    blank=True, null=True, verbose_name='Вложения запроса')),
                ('is_test_message', models.BooleanField(
                    default=False,
                    verbose_name='Признак тестового взаимодействия')),
            ],
            options={'abstract': False, }, ),
        migrations.CreateModel(
            name='PostProviderRequest',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('message_type', models.CharField(
                    max_length=100, verbose_name='Вид сведений')),
                ('message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор сообщения')),
                ('origin_message_id', models.CharField(
                    max_length=100,
                    null=True,
                    verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО'
                )),
                ('body', models.TextField(
                    verbose_name='Бизнес-данные запроса')),
                ('attachments', django.contrib.postgres.fields.jsonb.JSONField(
                    blank=True, null=True, verbose_name='Вложения запроса')),
                ('replay_to', models.CharField(
                    max_length=4000, verbose_name='Индекс сообщения в СМЭВ')),
                ('content_failure_code', models.CharField(
                    blank=True,
                    choices=[(b'ACCESS_DENIED', b'access denied'),
                             (b'UNKNOWN_REQUEST_DESCRIPTION',
                              b'unknown request description'),
                             (b'NO_DATA', b'no data'),
                             (b'FAILURE', b'failure')],
                    max_length=50,
                    null=True,
                    verbose_name='Код причины отказа')),
                ('content_failure_comment', models.TextField(
                    blank=True,
                    default=b'',
                    verbose_name='Пояснение причины отказа')),
                ('is_test_message', models.BooleanField(
                    default=False,
                    verbose_name='Признак тестового взаимодействия')),
            ],
            options={'abstract': False, }, ),
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', models.SmallIntegerField(
                    choices=[(1, b'not sent'), (2, b'sent'), (3, b'error')],
                    default=1,
                    verbose_name='Состояние пакетов')),
                ('error', models.TextField(
                    default=b'', verbose_name='Текст ошибки')),
                ('timestamp_created', models.DateTimeField(
                    auto_now_add=True, verbose_name='Время и дата запроса')),
                ('request_type', models.CharField(
                    choices=[
                        (b'delete/api/v0/as-provider/receipt/',
                         'Запрос на удаление полученных ответов от СМЭВ'),
                        (b'post/api/v0/as-consumer/request/',
                         'Передача заявок в СМЭВ'),
                        (b'delete/api/v0/as-consumer/response/',
                         'Запрос на удаление полученных ответов'),
                        (b'post/api/v0/as-provider/response/',
                         'Передача ответа на заявки'),
                        (b'delete/api/v0/as-provider/request/',
                         'Запрос на удаление полученных заявок'),
                        (b'get/api/v0/as-provider/receipt',
                         'Получение ответа СМЭВ по всем отправленным заявкам'),
                        (b'get/api/v0/as-consumer/response/',
                         'Получение всех ответов из очереди СМЭВ'),
                        (b'delete/api/v0/as-consumer/receipt/',
                         'Запрос на удаление квитанций СМЭВ по всем отправленным заявкам'
                         ), (b'get/api/v0/as-provider/request',
                             'Получение всех заявок к РИС'),
                        (b'get/api/v0/as-consumer/receipt',
                         'Получение квитанций СМЭВ по всем отправленным заявкам'
                         )
                    ],
                    default=b'get/api/v0/as-provider/request',
                    max_length=100,
                    verbose_name='Тип запроса')),
                ('sender_url', models.URLField(
                    max_length=400, verbose_name='URL запроса')),
                ('http_header', models.TextField(
                    default=b'{"Content-Type": "application/json;charset=utf-8"}',
                    verbose_name='Заголовок http запроса')),
                ('http_body', models.TextField(
                    verbose_name='Тело http запроса')),
            ],
            options={'abstract': False, }, ),
        migrations.AddField(
            model_name='postproviderrequest',
            name='request_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='aio_client.RequestLog',
                verbose_name='Лог запроса'), ),
        migrations.AddField(
            model_name='postconsumerrequest',
            name='request_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='aio_client.RequestLog',
                verbose_name='Лог запроса'), ),
        migrations.AddField(
            model_name='getproviderrequest',
            name='request_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='aio_client.RequestLog',
                verbose_name='Лог запроса'), ),
        migrations.AddField(
            model_name='getproviderreceipt',
            name='request_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='aio_client.RequestLog',
                verbose_name='Лог запроса'), ),
        migrations.AddField(
            model_name='getconsumerresponse',
            name='request_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='aio_client.RequestLog',
                verbose_name='Лог запроса'), ),
        migrations.AddField(
            model_name='getconsumerreceipt',
            name='request_id',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='aio_client.RequestLog',
                verbose_name='Лог запроса'), ),
    ]
