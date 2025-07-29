# coding: utf-8
import logging

from django.db.models import Q
from django.forms.models import model_to_dict

from aio_client.base import RequestLog

from .exceptions import ReceiptNotFound
from .exceptions import ResponseNotFound
from .helpers import provider_post_request
from .models import GetProviderReceipt
from .models import GetProviderRequest
from .models import PostProviderRequest


def _get_requests_by_filter(q_filter):
    """Получение заявок к РИС по любому фильтру.
    После получения они помечаются отправленными.

    :param q_filter: фильтр заявок
    :type q_filter: Q
    :return: Список запросов к РИС как к поставщику услуг
    :rtype: list[dict]
    """
    qs = GetProviderRequest.objects.filter(
        q_filter,
    ).exclude(
        state=GetProviderRequest.SENT,
    ).order_by('id')

    result = list(qs.values('id', *GetProviderRequest.LIST_AIO_FIELDS))
    GetProviderRequest.objects.filter(
        id__in=tuple(r['id'] for r in result)
    ).update(state=GetProviderRequest.SENT)

    return result


# deprecated с 1.8.9; следует использовать get_requests_by_message_types
def get_requests(message_type=None):
    """Получение всех заявок к РИС.
    После получения они помечаются отправленными.

    :param message_type: Вид сведений, необязательный параметр,
    если не передается, отдаем все запросы
    :return: Список запросов к РИС как к поставщику услуг
    """
    logging.warning(
        u'%s.%s устарел. Рекомендуется использовать %s.%s',
        __name__,
        get_requests.__name__,
        __name__,
        get_requests_by_message_types.__name__,
    )

    q_filter = Q(message_type=message_type) if message_type is not None else Q()

    return _get_requests_by_filter(q_filter)


def get_requests_by_message_types(*, message_types):
    """Получение заявок к РИС.
    После получения они помечаются отправленными.

    :param message_types: Виды сведений. Если переданы, будут отобраны
    только те заявки, у которых message_type совпадает с переданными
    :return: Список запросов к РИС как к поставщику услуг
    :rtype: list[dict]
    """
    q_filter = Q(message_type__in=message_types)

    return _get_requests_by_filter(q_filter)


def set_error_requests(origin_message_ids):
    """Указывает признак ошибки при обработке сообщения.

    Применяется для повторного получения сообщения в get_requests.

    :param origin_message_ids: Список origin_message_id
    :return: Количество измененных записей
    """
    assert isinstance(origin_message_ids, list)
    qs = GetProviderRequest.objects.filter(
        origin_message_id__in=origin_message_ids)

    return qs.update(state=GetProviderRequest.ERROR)


def push_request(message):
    """Передает ответ на запрос услуги.

    :param message: Запись aio_client.provider.models.PostProviderRequest
    :return: Инстанс класса requests.models.Response
    """
    assert isinstance(message, PostProviderRequest)
    response = provider_post_request(message)

    return response


def get_response(origin_message_id):
    """Запрос ответа от СМЭВ в ответ на запрос услуги.

    :param str origin_message_id: Идентификатор сообщения
    :return: Словарь со списком полей GetProviderReceipt.LIST_AIO_FIELDS
    """
    qs_response = PostProviderRequest.objects.filter(
        origin_message_id=origin_message_id,
        request_id__state=RequestLog.SENT)
    if not qs_response.exists():
        raise ResponseNotFound(
            message=ResponseNotFound.DEFAULT_MSG % origin_message_id)

    receipt = GetProviderReceipt.objects.filter(
        origin_message_id=origin_message_id).order_by('id').last()
    if not receipt:
        raise ReceiptNotFound(
            message=ReceiptNotFound.DEFAULT_MSG % origin_message_id)

    return model_to_dict(receipt, GetProviderReceipt.LIST_AIO_FIELDS)
