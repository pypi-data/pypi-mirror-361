# coding: utf-8
from django.apps import AppConfig


class AioClientConfig(AppConfig):

    name = 'aio_client'
    label = 'aio_client'
    verbose_name = u"Клиент АИО"

    def ready(self):
        from aio_client.provider import tasks
        from aio_client.consumer import tasks
