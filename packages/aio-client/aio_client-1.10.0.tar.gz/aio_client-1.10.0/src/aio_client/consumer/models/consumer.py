# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.db.models import OuterRef
from django.db.models import Max
from django.db.models import Subquery

from aio_client.base.const import FAILURE_CODES
from aio_client.base.models import GetReceipt
from aio_client.base.models import RequestLog
from aio_client.base.models import RequestMessage


class PostConsumerRequestManager(models.Manager):

    def not_sent(self):
        """Получаем те записи об отправке сообщения,
        где последняя попытка не удачная, статус НЕ ОТПРАВЛЕН"""
        # Список записей о последней попытке отправки сообщений
        # получаем те записи об отправке сообщения,
        # где последняя попытка не удачная

        qs_last_requests = PostConsumerRequest.objects.values(
            'message_id'
        ).filter(
            message_id=OuterRef('message_id')
        ).annotate(max_id=Max('id')).values('max_id')

        qs_errors = PostConsumerRequest.objects.filter(
            request_id__state=RequestLog.NOT_SENT,
            id__in=Subquery(qs_last_requests),
        ).exclude(
            request_id__error__exact='',
        )
        return qs_errors


class PostConsumerRequest(RequestMessage):
    """Передача заявок в СМЭВ"
    message_id Уникальный идентификатор запроса с типом данных UUID,
    который формируется в РИС по  RFC 4122 первого типа.
    """
    NAME_ID_FIELD = "message_id"
    LIST_AIO_FIELDS = [
        "message_id",
        "body",
        "attachments",
        "message_type",
        "is_test_message",
    ]
    is_test_message = models.BooleanField(
        default=False, verbose_name='Признак тестового взаимодействия')
    # Стандартный менеджер.
    objects = PostConsumerRequestManager()

    class Meta:
        verbose_name = 'Потребитель. Заявка в СМЭВ'
        verbose_name_plural = 'Потребитель. Заявки в СМЭВ'


class GetConsumerResponse(RequestMessage):
    """Ответы из очереди СМЭВ"""

    LIST_AIO_FIELDS = [
        "message_id",
        "origin_message_id",
        "body",
        "attachments",
        "message_type",
        "content_failure_code",
        "content_failure_comment",
    ]

    content_failure_code = models.CharField(
        verbose_name='Код ошибки',
        max_length=50,
        choices=FAILURE_CODES,
        null=True,
        blank=True,
    )

    content_failure_comment = models.TextField(
        verbose_name='Описание ошибки',
        default='',
        null=True,
    )

    class Meta:
        verbose_name = 'Потребитель. Ответ СМЭВ'
        verbose_name_plural = 'Потребитель. Ответы СМЭВ'


class GetConsumerReceipt(GetReceipt):
    """Квитанций с результатом отправки запроса.

    В реестре "Потребитель. Ответ СМЭВ по заявкам" у сообщений должен
    становиться статус "Отправлено" после того,
    как сообщение успешно обработает РИС или "Ошибка",
    если при обработке возникнут ошибки.
    """
    LIST_AIO_FIELDS = (
        "message_id",
        "error",
        "origin_message_id",
        "fault",
        "message_type",
    )

    class Meta:
        verbose_name = 'Потребитель. Ответ СМЭВ по заявкам'
        verbose_name_plural = 'Потребитель. Ответы СМЭВ по заявкам'
