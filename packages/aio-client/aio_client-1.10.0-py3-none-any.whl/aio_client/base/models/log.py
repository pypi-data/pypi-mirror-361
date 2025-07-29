# coding: utf-8
import json
import six

from django.db import models

from .base import AbstractStateModel
from .enum import DEL
from .enum import POST
from .enum import RequestTypeEnum

if six.PY3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


class RequestLog(AbstractStateModel):
    JSON_HEADER = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    # поле содержит иноформацию об ошибке,
    # которая произошла в процессе передачи данных
    error = models.TextField(default='', verbose_name=u"Текст ошибки запроса")

    # Поле содержит http-ответ от АИО, при котором возникла ошибка
    error_http_body = models.TextField(
        verbose_name=u"Тело http ответа при возникновении ошибки",
        default='', null=True,
    )

    timestamp_created = models.DateTimeField(
        auto_now_add=True, verbose_name=u"Время и дата запроса")
    request_type = models.CharField(
        max_length=100,
        choices=RequestTypeEnum.get_choices(),
        default=RequestTypeEnum.PR_GET,
        verbose_name=u"Тип запроса")
    sender_url = models.URLField(max_length=400, verbose_name=u"URL запроса")
    http_header = models.TextField(
        default=json.dumps(JSON_HEADER), verbose_name=u"Заголовок http запроса")
    http_body = models.TextField(verbose_name=u"Тело http запроса")

    def get_request_params(self):
        """Получение параметров для запроса.

        :return: Словарь с параметрами запроса
        :rtype: dict
        """
        params = dict(
            method=RequestTypeEnum.get_function(self.request_type),
            url=self.sender_url,
            headers=self.http_header,
        )
        if params['method'] == POST:
            params['json'] = self.http_body
        elif params['method'] == DEL:
            # Ожидаем, что в self.http_body будет содержаться id записи,
            # либо json с параметрами для множественного удаления
            try:
                http_body = json.loads(self.http_body)
            except (ValueError, TypeError):
                http_body = self.http_body

            if isinstance(http_body, dict):
                # Удаление нескольких записей по параметрам
                params['params'] = http_body
            else:
                # Url для удаления одной записи
                params['url'] = urljoin(
                    self.sender_url, '{}/'.format(http_body)
                )

        return params

    class Meta:
        verbose_name = u'HTTP запрос'
        verbose_name_plural = u'HTTP запросы'


RequestLog._meta.get_field('state').verbose_name = u"Статус запроса"
