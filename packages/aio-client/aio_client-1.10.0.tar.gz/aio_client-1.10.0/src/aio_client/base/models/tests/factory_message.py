# coding: utf-8
import factory

from aio_client.base.models.message import RequestMessage

from .factory_log import RequestLogF


class RequestMessageF(factory.DjangoModelFactory):

    class Meta:
        model = RequestMessage

    request_id = factory.SubFactory(RequestLogF)
