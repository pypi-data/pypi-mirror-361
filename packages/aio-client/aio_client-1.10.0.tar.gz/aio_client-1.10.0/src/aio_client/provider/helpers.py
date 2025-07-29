# coding: utf-8

from django.db import IntegrityError

from aio_client.base import RequestTypeEnum
from aio_client.base import _prepare_log
from aio_client.base import send_request
from aio_client.base.helpers import capture_message
from aio_client.base.helpers import post_request
from aio_client.base.signals import get_data_done
from aio_client.base.signals import robust_sender

from .models import GetProviderReceipt
from .models import GetProviderRequest
from .models import PostProviderRequest


@robust_sender(get_data_done, sender=GetProviderRequest)
def provider_get_requests(values=None, title=''):
    """Получение всех заявок к РИС.

    :param values: Cловарь с ходом выполнения асинк. задачи;
    :type values: dict[str, str]
    :param title: Наименование шага выполнения;
    :type title: str

    :return: Cписок словарей с параметрами ответа.
    :rtype: list

    """

    is_send_signal = False

    request_log = _prepare_log(RequestTypeEnum.PR_GET)

    response = send_request(request_log)
    for message in response.json():
        message['request_id'] = request_log

        try:
            GetProviderRequest.objects.create(**message)
        except IntegrityError as err:
            error_message = (
                f'Не удалось создать сообщение GetProviderRequest'
                f'({message["message_id"]}:{message["origin_message_id"]})  - {err}')

            if values:
                values[title] = error_message
        else:
            is_send_signal = True

    return response.json(), is_send_signal


def provider_post_request(request_msg):
    """Передача ответа на заявки
    :param request_msg: объект класса PostProviderRequest
     c параметрами ответа
    :return: инстанс класса requests.models.Response
    """
    assert isinstance(request_msg, PostProviderRequest)
    return post_request(request_msg)


@robust_sender(get_data_done, sender=GetProviderReceipt)
def provider_get_receipt(values=None, title=''):
    """Получение ответа СМЭВ по всем отправленным заявкам.

    :param values: Cловарь с ходом выполнения асинк. задачи;
    :type values: dict[str, str]
    :param title: Наименование шага выполнения;
    :type title: str

    :return: Cписок словарей с параметрами ответа.
    :rtype: list

    """

    is_send_signal = False

    request_log = _prepare_log(RequestTypeEnum.PR_GET_R)

    response = send_request(request_log)
    for message in response.json():
        message['request_id'] = request_log

        try:
            GetProviderReceipt.objects.create(**message)
        except IntegrityError as err:
            error_message = (
                f'Не удалось создать сообщение GetProviderReceipt'
                f'({message["message_id"]}:{message["origin_message_id"]}) - {err}')

            if values:
                values[title] = error_message
        else:
            is_send_signal = True

    return response.json(), is_send_signal
