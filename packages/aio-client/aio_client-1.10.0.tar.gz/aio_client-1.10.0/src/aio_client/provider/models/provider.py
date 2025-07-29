# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.db.models import OuterRef
from django.db.models import Max
from django.db.models import Subquery

from aio_client.base.const import ACCESS_DENIED
from aio_client.base.const import FAILURE
from aio_client.base.const import FAILURE_CODES
from aio_client.base.const import NO_DATA
from aio_client.base.const import UNKNOWN_REQUEST_DESCRIPTION

from aio_client.base.models import GetReceipt
from aio_client.base.models import RequestLog
from aio_client.base.models import RequestMessage


class GetProviderRequest(RequestMessage):
    """ответ на запрос получение всех заявок к РИС"""
    # Список полей приходящих из АИО
    NOT_SENT = 1
    SENT = 2
    ERROR = 3

    STATE = (
        (NOT_SENT, 'Не отправлен в РИС'),
        (SENT, 'Отправлен в РИС'),
        (ERROR, 'Ошибка'),
    )
    LIST_AIO_FIELDS = (
        "message_id",
        "origin_message_id",
        "body",
        "attachments",
        "is_test_message",
        "replay_to",
        "message_type")

    is_test_message = models.BooleanField(
        default=False, verbose_name='Признак тестового взаимодействия')
    replay_to = models.CharField(
        max_length=4000, verbose_name='Индекс сообщения в СМЭВ')

    class Meta:
        verbose_name = 'Поставщик. Заявка от СМЭВ'
        verbose_name_plural = 'Поставщик. Заявки от СМЭВ'


GetProviderRequest._meta.get_field('state').choices = GetProviderRequest.STATE
GetProviderRequest._meta.get_field('state').default = (
    GetProviderRequest.NOT_SENT
)


class PostProviderRequestManager(models.Manager):

    def not_sent(self):
        """Получаем те записи об отправке сообщения,
        где последняя попытка не удачная, статус НЕ ОТПРАВЛЕН"""
        # Список записей о последней попытке отправки сообщений
        # получаем те записи об отправке сообщения,
        # где последняя попытка не удачная
        qs_last_requests = PostProviderRequest.objects.values(
            'origin_message_id'
        ).filter(
            origin_message_id=OuterRef('origin_message_id')
        ).annotate(max_id=Max('id')).values('max_id')

        qs_errors = PostProviderRequest.objects.filter(
            id__in=Subquery(qs_last_requests),
            request_id__state=RequestLog.NOT_SENT,
        ).exclude(
            request_id__error__exact='')

        return qs_errors


class PostProviderRequest(RequestMessage):
    """ответ РИС как поставщика на заявку из АИО"""
    # Список полей в сообщение, которые ожидает АИО
    LIST_AIO_FIELDS = (
        "origin_message_id",
        "body",
        "message_type",
        "attachments",
        "content_failure_code",
        "content_failure_comment",
        "replay_to",
        "is_test_message"
    )

    # Публичные атрибуты
    # Добавлены для обратной совместимости с РИС
    # TODO после полного перехода РИС на использование aio_client >= 1.5.0 удалить их
    ACCESS_DENIED = ACCESS_DENIED
    UNKNOWN_REQUEST_DESCRIPTION = UNKNOWN_REQUEST_DESCRIPTION
    NO_DATA = NO_DATA
    FAILURE = FAILURE

    FAILURE_CODES = FAILURE_CODES

    # используется как "обратный адрес" при передаче ответа на заявку
    replay_to = models.CharField(
        max_length=4000, verbose_name='Индекс сообщения в СМЭВ')
    content_failure_code = models.CharField(
        max_length=50,
        choices=FAILURE_CODES,
        null=True,
        blank=True,
        verbose_name='Код причины отказа'
    )
    content_failure_comment = models.TextField(
        default='', blank=True, verbose_name='Пояснение причины отказа')
    is_test_message = models.BooleanField(
        default=False, verbose_name='Признак тестового взаимодействия')
    # Стандартный менеджер.
    objects = PostProviderRequestManager()

    class Meta:
        verbose_name = 'Поставщик. Ответ на заявку'
        verbose_name_plural = 'Поставщик. Ответы на заявку'


class GetProviderReceipt(GetReceipt):
    """Ответы из очереди СМЭВ"""
    # Список полей приходящих из АИО
    LIST_AIO_FIELDS = (
        "message_id",
        "error",
        "origin_message_id",
        "fault",
        "message_type",
    )

    class Meta:
        verbose_name = 'Поставщик. Ответ СМЭВ по заявкам'
        verbose_name_plural = 'Поставщик. Ответы СМЭВ по заявкам'
