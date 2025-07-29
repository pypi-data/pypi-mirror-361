# coding: utf-8

import factory

from aio_client.base.models.log import RequestLog


class RequestLogF(factory.DjangoModelFactory):
    class Meta:
        model = RequestLog
