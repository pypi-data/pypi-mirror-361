# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0005_auto_20200703_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='getconsumerresponse',
            name='content_failure_code',
            field=models.CharField(blank=True,
                                   choices=[('ACCESS_DENIED', 'access denied'),
                                            ('UNKNOWN_REQUEST_DESCRIPTION',
                                             'unknown request description'),
                                            ('NO_DATA', 'no data'),
                                            ('FAILURE', 'failure')],
                                   max_length=50,
                                   null=True,
                                   verbose_name='Код ошибки'),
        ),
        migrations.AddField(
            model_name='getconsumerresponse',
            name='content_failure_comment',
            field=models.TextField(default='',
                                   null=True,
                                   verbose_name='Описание ошибки'),
        ),
    ]
