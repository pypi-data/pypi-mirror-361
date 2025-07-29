# coding: utf-8

from aio_client.base.models.tests.factory_message import RequestMessageF

from ..provider import GetProviderReceipt
from ..provider import GetProviderRequest
from ..provider import PostProviderRequest


class GetProviderRequestF(RequestMessageF):

    class Meta:
        model = GetProviderRequest


class PostProviderRequestF(RequestMessageF):

    class Meta:
        model = PostProviderRequest


class GetProviderReceiptF(RequestMessageF):

    class Meta:
        model = GetProviderReceipt
