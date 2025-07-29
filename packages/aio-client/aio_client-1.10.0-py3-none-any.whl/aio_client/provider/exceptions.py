# coding: utf-8

from aio_client.base.exceptions import AioClientException


class ProviderException(AioClientException):
    """Исключения из модуля aio_client.provider"""
    DEFAULT_CODE = u'provider_err'
    DEFAULT_MSG = u'Исключения из модуля aio_client.provider'


class ResponseNotFound(ProviderException):
    DEFAULT_CODE = u'response_not_found'
    DEFAULT_MSG = (u'По origin_message_id=%s не найдено отправленных '
                   u'ответов в СМЭВ')


class ReceiptNotFound(ProviderException):
    DEFAULT_CODE = u'receipt_not_found'
    DEFAULT_MSG = u'По origin_message_id=%s не найдено ответа от СМЭВ'
