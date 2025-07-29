from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('aio_client', '0011_auto_20210416_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getconsumerreceipt',
            name='origin_message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                unique=True,
                verbose_name=
                'Уникальный идентификатор цепочки взаимодействия в АИО'),
        ),
        migrations.AlterField(
            model_name='getconsumerresponse',
            name='origin_message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                unique=True,
                verbose_name=
                'Уникальный идентификатор цепочки взаимодействия в АИО'),
        ),
        migrations.AlterField(
            model_name='getproviderreceipt',
            name='origin_message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                unique=True,
                verbose_name=
                'Уникальный идентификатор цепочки взаимодействия в АИО'),
        ),
        migrations.AlterField(
            model_name='getproviderrequest',
            name='origin_message_id',
            field=models.CharField(
                db_index=True,
                max_length=100,
                null=True,
                unique=True,
                verbose_name=
                'Уникальный идентификатор цепочки взаимодействия в АИО'),
        ),
    ]
