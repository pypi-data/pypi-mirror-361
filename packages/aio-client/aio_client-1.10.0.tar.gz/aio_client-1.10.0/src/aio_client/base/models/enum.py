# coding: utf-8

import six

from aio_client import configs as aio_client_settings


if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


#типы запросов
GET = 'get'
DEL = 'delete'
POST = 'post'


class BaseEnumerate(object):
    """Базовый класс для создания перечислений."""
    # В словаре values описываются перечисляемые константы
    # и их человеческое название
    # Например: {STATE1: u'Состояние 1', CLOSED: u'Закрыто'}
    values = {}

    @classmethod
    def get_choices(cls):
        """
        Используется для ограничения полей ORM и в качестве источника данных
        в ArrayStore и DataStore ExtJS
        """
        return list(cls.values.items())

    get_items = get_choices

    @classmethod
    def get_constant_value_by_name(cls, name):
        """
        Возвращает значение атрибута константы, которая используется в
        качестве ключа к словарю values
        """
        if not isinstance(name, six.string_types):
            raise TypeError("'name' must be a string")

        if not name:
            raise ValueError("'name' must not be empty")

        return cls.__dict__[name]


class RequestTypeEnum(BaseEnumerate):
    u"""Типы запросов."""

    PR_GET = '%s/api/v0/as-provider/request/' % GET
    PR_DEL = '%s/api/v0/as-provider/request/' % DEL
    PR_POST = '%s/api/v0/as-provider/response/' % POST
    PR_GET_R = '%s/api/v0/as-provider/receipt/' % GET
    PR_DEL_R = '%s/api/v0/as-provider/receipt/' % DEL
    CS_POST = '%s/api/v0/as-consumer/request/' % POST
    CS_GET_R = '%s/api/v0/as-consumer/receipt/' % GET
    CS_DEL_R = '%s/api/v0/as-consumer/receipt/' % DEL
    CS_GET = '%s/api/v0/as-consumer/response/' % GET
    CS_DEL = '%s/api/v0/as-consumer/response/' % DEL

    values = {
        PR_GET: u"Поставщик.Получение всех заявок к РИС",
        PR_DEL: u"Поставщик.Запрос на удаление полученных заявок",
        PR_POST: u"Поставщик.Передача ответа на заявки",
        PR_GET_R: u"Поставщик.Получение ответа СМЭВ по всем отправленным"
                  u" заявкам",
        PR_DEL_R: u"Поставщик.Запрос на удаление полученных ответов от СМЭВ",
        CS_POST: u'Потребитель.Передача заявок в СМЭВ',
        CS_GET_R: u'Потребитель.Получение ответа СМЭВ по всем отправленным '
                  u'заявкам',
        CS_DEL_R: u'Потребитель.Запрос на удаление полученных ответов от СМЭВ',
        CS_GET: u'Потребитель.Получение всех ответов из очереди СМЭВ',
        CS_DEL: u'Потребитель.Запрос на удаление полученных ответов',
    }

    @classmethod
    def get_url(cls, request_type):
        """ Возвращает полный путь до эндпоинта АИО

        :param request_type:
        :return:
        """
        if request_type not in cls.values:
            return None
        return urljoin(
            aio_client_settings.AIO_SERVER,
            '/'.join(request_type.split('/')[1:])
        )

    @classmethod
    def get_function(cls, request_type):
        """Возвращает тип запроса get/post/delete.

        :param request_type:
        :return: Тип запроса в текстовом представление
        :rtype: str
        """
        if request_type not in cls.values:
            return None
        return request_type.split('/')[0]
