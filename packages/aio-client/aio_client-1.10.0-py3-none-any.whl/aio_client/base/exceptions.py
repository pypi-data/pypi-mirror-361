# coding: utf-8


class AioClientException(Exception):
    """Ошибки, генерируемые в модуле aio_client"""
    DEFAULT_CODE = u''
    DEFAULT_MSG = u''

    def __init__(self, code=None, message=None):
        self.code = code or self.DEFAULT_CODE
        self.message = message or self.DEFAULT_MSG


class TransportException(AioClientException):
    """Ошибки транспортного уровня."""
    DEFAULT_MSG = u'Не удалось установить соединение'


class HttpErrorException(AioClientException):
    """HTTP error при отправке, сообщение не отправлено
    """
    DEFAULT_MSG = u'Не удалось отправить запрос'


class HttpFailureException(AioClientException):
    """Код ответа не 200, но сообщение ушло"""
    DEFAULT_MSG = u'Ответ со статусом ошибки'
