# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0010_auto_20210416_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getconsumerreceipt',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
        migrations.AlterField(
            model_name='getconsumerresponse',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
        migrations.AlterField(
            model_name='getproviderreceipt',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
        migrations.AlterField(
            model_name='getproviderrequest',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен в РИС'),
                                                    (2, 'Отправлен в РИС'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
        migrations.AlterField(
            model_name='postconsumerrequest',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
        migrations.AlterField(
            model_name='postproviderrequest',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
        migrations.AlterField(
            model_name='requestlog',
            name='state',
            field=models.SmallIntegerField(choices=[(1, 'Не отправлен'),
                                                    (2, 'Отправлен'),
                                                    (3, 'Ошибка')],
                                           db_index=True,
                                           default=1,
                                           verbose_name='Статус сообщения'),
        ),
    ]
