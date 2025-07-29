# coding: utf-8

from aio_client.base.exceptions import AioClientException


class ConsumerException(AioClientException):
    """Исключения из модуля aio_client.consumer"""
    DEFAULT_CODE = u'consumer_err'
    DEFAULT_MSG = u'Исключения из модуля aio_client.consumer'


class RequestNotFound(ConsumerException):
    DEFAULT_CODE = u'request_not_found'
    DEFAULT_MSG = (u'По origin_message_id=%s не найдено отправленных '
                   u'запросов в СМЭВ')
