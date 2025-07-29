# coding: utf-8

from aio_client.base.models.tests.factory_message import RequestMessageF

from ..consumer import PostConsumerRequest


class PostConsumerRequestF(RequestMessageF):

    class Meta:
        model = PostConsumerRequest
