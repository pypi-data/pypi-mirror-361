# coding: utf-8
from django.db import models

from .base import AbstractStateModel
from .log import RequestLog


class AbstractMessage(AbstractStateModel):
    """Базовый класс сообщений."""

    request_id = models.ForeignKey(
        RequestLog,
        verbose_name='Лог запроса',
        on_delete=models.CASCADE,
    )
    message_type = models.CharField(
        max_length=100,
        verbose_name='Вид сведений',
    )
    message_id = models.CharField(
        max_length=100,
        null=True,
        unique=True,
        db_index=True,
        verbose_name='Уникальный идентификатор сообщения',
    )
    origin_message_id = models.CharField(
        max_length=100,
        null=True,
        db_index=True,
        verbose_name='Уникальный идентификатор цепочки взаимодействия в АИО',
    )

    class Meta:
        abstract = True
        ordering = ['-id', ]

    def __str__(self):
        return '{0} - {1}'.format(self.message_id or '',
                                  self.origin_message_id or '')


class RequestMessage(AbstractMessage):
    """Базовый класс сообщений ответов и запросов."""

    NAME_ID_FIELD = 'origin_message_id'

    body = models.TextField(verbose_name='Бизнес-данные запроса')
    attachments = models.JSONField(
        verbose_name='Вложения запроса', blank=True, null=True)

    class Meta:
        abstract = True


class GetReceipt(AbstractMessage):
    """Базовый класс сообщений квитанций ответов от СМЭВ."""

    NAME_ID_FIELD = 'origin_message_id'

    error = models.TextField(
        default='',
        verbose_name='Сообщение об ошибке, возникшей при передаче данных в СМЭВ',
    )
    fault = models.BooleanField(
        default=False,
        verbose_name='Признак успешного взаимодействия',
    )

    class Meta:
        abstract = True
