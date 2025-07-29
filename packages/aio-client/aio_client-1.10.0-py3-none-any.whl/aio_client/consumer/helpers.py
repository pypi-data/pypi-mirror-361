# coding: utf-8

import datetime

from django.db import IntegrityError

from aio_client.base import RequestTypeEnum
from aio_client.base import _prepare_log
from aio_client.base import send_request
from aio_client.base.helpers import capture_message
from aio_client.base.helpers import create_message_id
from aio_client.base.helpers import post_request
from aio_client.base.signals import get_data_done
from aio_client.base.signals import robust_sender

from .const import CHANGE_MESSAGE_ID_IN_DAYS
from .models import GetConsumerReceipt
from .models import GetConsumerResponse
from .models import PostConsumerRequest


@robust_sender(get_data_done, sender=GetConsumerResponse)
def consumer_get_requests(values=None, title=''):
    """Получение всех ответов из очереди СМЭВ.

    :param values: Cловарь с ходом выполнения асинк. задачи;
    :type values: dict[str, str]
    :param title: Наименование шага выполнения;
    :type title: str

    :return: Cписок словарей с параметрами ответа.
    :rtype: list

    """

    is_send_signal = False

    request_log = _prepare_log(RequestTypeEnum.CS_GET)

    response = send_request(request_log)
    for message in response.json():
        message['request_id'] = request_log

        try:
            GetConsumerResponse.objects.create(**message)
        except IntegrityError:
            error_message = (
                f'Не удалось создать сообщение GetConsumerResponse'
                f'({message["message_id"]}:{message["origin_message_id"]})')

            if values:
                values[title] = error_message
        else:
            is_send_signal = True

    return response.json(), is_send_signal


def consumer_post_request(request_msg):
    """Передача заявок в СМЭВ

    Если сообщение отправляется повторно, то создаем message_id заново
    :param request_msg: объект класса PostConsumerRequest
     c параметрами ответа
    :return: инстанс класса requests.models.Response, либо None
    """
    assert isinstance(request_msg, PostConsumerRequest)
    if hasattr(request_msg, 'request_id'):
        diff_in_days = abs(
            request_msg.request_id.timestamp_created - datetime.datetime.now()
        ).days
        if diff_in_days >= CHANGE_MESSAGE_ID_IN_DAYS:
            request_msg.message_id = create_message_id()
    return post_request(request_msg)


@robust_sender(get_data_done, sender=GetConsumerReceipt)
def consumer_get_receipt(values=None, title=''):
    """Получение ответа СМЭВ по всем отправленным заявкам.

    :param values: Cловарь с ходом выполнения асинк. задачи;
    :type values: dict[str, str]
    :param title: Наименование шага выполнения;
    :type title: str

    :return: Cписок словарей с параметрами ответа.
    :rtype: list

    """

    is_send_signal = False

    request_log = _prepare_log(RequestTypeEnum.CS_GET_R)

    response = send_request(request_log)
    for message in response.json():
        message.update(
            request_id=request_log,
            state=GetConsumerReceipt.SENT)

        try:
            GetConsumerReceipt.objects.create(**message)
        except IntegrityError:
            error_message = (
                f'Не удалось создать сообщение GetConsumerReceipt'
                f'({message["message_id"]}:{message["origin_message_id"]})')

            if values:
                values[title] = error_message
        else:
            is_send_signal = True

    return response.json(), is_send_signal
