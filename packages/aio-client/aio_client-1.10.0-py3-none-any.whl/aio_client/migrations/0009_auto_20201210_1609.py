# coding: utf-8
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0008_auto_20201209_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='error_http_body',
            field=models.TextField(
                default='',
                null=True,
                verbose_name='Тело http ответа при возникновении ошибки'),
        ),
    ]
