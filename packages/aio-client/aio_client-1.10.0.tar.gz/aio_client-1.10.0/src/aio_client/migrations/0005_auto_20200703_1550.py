# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0004_auto_20200703_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getconsumerreceipt',
            name='message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                verbose_name='Уникальный идентификатор сообщения'),
        ),
        migrations.AlterField(
            model_name='getconsumerreceipt',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
        migrations.AlterField(
            model_name='getconsumerresponse',
            name='message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                verbose_name='Уникальный идентификатор сообщения'),
        ),
        migrations.AlterField(
            model_name='getconsumerresponse',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
        migrations.AlterField(
            model_name='getproviderreceipt',
            name='message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                verbose_name='Уникальный идентификатор сообщения'),
        ),
        migrations.AlterField(
            model_name='getproviderreceipt',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
        migrations.AlterField(
            model_name='getproviderrequest',
            name='message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                verbose_name='Уникальный идентификатор сообщения'),
        ),
        migrations.AlterField(
            model_name='getproviderrequest',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен в РИС'),
                                                    (2, 'Отправлен в РИС'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
        migrations.AlterField(
            model_name='postconsumerrequest',
            name='message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                verbose_name='Уникальный идентификатор сообщения'),
        ),
        migrations.AlterField(
            model_name='postconsumerrequest',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
        migrations.AlterField(
            model_name='postproviderrequest',
            name='message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                verbose_name='Уникальный идентификатор сообщения'),
        ),
        migrations.AlterField(
            model_name='postproviderrequest',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Состояние пакетов'),
        ),
    ]
