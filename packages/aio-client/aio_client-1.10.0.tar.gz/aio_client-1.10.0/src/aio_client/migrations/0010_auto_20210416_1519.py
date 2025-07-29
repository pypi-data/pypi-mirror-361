# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0009_auto_20201210_1609'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='getconsumerreceipt',
            options={
                'verbose_name': 'Потребитель. Ответ СМЭВ по заявкам',
                'verbose_name_plural': 'Потребитель. Ответы СМЭВ по заявкам'
            },
        ),
        migrations.AlterModelOptions(
            name='getconsumerresponse',
            options={
                'verbose_name': 'Потребитель. Ответ СМЭВ',
                'verbose_name_plural': 'Потребитель. Ответы СМЭВ'
            },
        ),
        migrations.AlterModelOptions(
            name='getproviderreceipt',
            options={
                'verbose_name': 'Поставщик. Ответ СМЭВ по заявкам',
                'verbose_name_plural': 'Поставщик. Ответы СМЭВ по заявкам'
            },
        ),
        migrations.AlterModelOptions(
            name='getproviderrequest',
            options={
                'verbose_name': 'Поставщик. Заявка от СМЭВ',
                'verbose_name_plural': 'Поставщик. Заявки от СМЭВ'
            },
        ),
        migrations.AlterModelOptions(
            name='postconsumerrequest',
            options={
                'verbose_name': 'Потребитель. Заявка в СМЭВ',
                'verbose_name_plural': 'Потребитель. Заявки в СМЭВ'
            },
        ),
        migrations.AlterModelOptions(
            name='postproviderrequest',
            options={
                'verbose_name': 'Поставщик. Ответ на заявку',
                'verbose_name_plural': 'Поставщик. Ответы на заявку'
            },
        ),
    ]
