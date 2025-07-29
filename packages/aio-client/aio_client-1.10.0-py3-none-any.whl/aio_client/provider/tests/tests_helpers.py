# coding: utf-8
from copy import deepcopy
import json

from django.test import TestCase
import six

from aio_client.base import RequestLog
from aio_client.base import RequestTypeEnum
from aio_client.base.models.tests.utils import mock_request_not_error
from aio_client.provider.helpers import _prepare_log
from aio_client.provider.models import GetProviderReceipt
from aio_client.provider.models import GetProviderRequest
from aio_client.provider.models import PostProviderRequest
from aio_client.provider.models.tests.factory_provider import \
    PostProviderRequestF
import aio_client

from .request_data import TEST_GET_PROVIDER_RECEIPT_EXAMPLE
from .request_data import TEST_GET_PROVIDER_RECEIPT_MESSAGE_ID
from .request_data import TEST_GET_PROVIDER_REQUEST_EXAMPLE
from .request_data import TEST_GET_PROVIDER_REQUEST_MESSAGE_ID


if six.PY2:
    import mock
else:
    from unittest import mock


class HelpersTestCase(TestCase):

    def setUp(self):
        self.request_type = RequestTypeEnum.PR_GET

    def tests_prepare_log(self):
        self.request_log = _prepare_log(self.request_type)

        self.assertIsInstance(self.request_log, RequestLog)
        self.assertEqual(self.request_log.request_type, self.request_type)
        self.assertEqual(self.request_log.http_header, RequestLog.JSON_HEADER)
        self.assertEqual(self.request_log.sender_url,
                         RequestTypeEnum.get_url(self.request_type))

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_provider_get_requests_empty(self, sender):
        """Проверяем обработку пустого ответа"""
        mock_resp = json.loads('[]')
        sender.return_value = mock.Mock(ok=True)
        sender.return_value.json.return_value = mock_resp

        response = aio_client.provider.helpers.provider_get_requests()
        # в ответе нет заявок
        self.assertEqual(len(response), 0)
        self.assertEqual(GetProviderRequest.objects.all().count(), 0)

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_provider_get_requests(self, sender):
        """Если ответ не пуст, то сообщение должно попасть в БД"""
        mock_resp = json.loads(TEST_GET_PROVIDER_REQUEST_EXAMPLE)
        return_value = mock.Mock(ok=True)
        return_value.json.return_value = mock_resp
        sender.side_effect = mock_request_not_error(return_value)

        response = aio_client.provider.helpers.provider_get_requests()
        # в ответе 1 заявка
        self.assertEqual(len(response), 1)
        # в таблице 1 заявка
        self.assertEqual(GetProviderRequest.objects.all().count(), 1)
        # заявка из файла GetProviderRequest.json
        self.assertEqual(response[0]['message_id'],
                         TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_provider_post_request(self, sender):
        """Проверка что запрос успешно ушел и попал в БД"""
        request_msg = PostProviderRequestF(
            origin_message_id=TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=200))
        response = aio_client.provider.helpers.provider_post_request(
            request_msg)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostProviderRequest.objects.all().count(), 1)
        self.assertEqual(
            PostProviderRequest.objects.all()[0].origin_message_id,
            TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_provider_get_receipt(self, sender):
        """Проверка что запрос успешно ушел и попал в БД"""
        mock_resp = json.loads(TEST_GET_PROVIDER_RECEIPT_EXAMPLE)
        return_value = mock.Mock(ok=True)
        return_value.json.return_value = mock_resp
        sender.side_effect = mock_request_not_error(return_value)

        response = aio_client.provider.helpers.provider_get_receipt()
        # в ответе 1 заявка
        self.assertEqual(len(response), 1)
        # в таблице 1 заявка
        self.assertEqual(GetProviderReceipt.objects.all().count(), 1)
        self.assertEqual(response[0]['message_id'],
                         TEST_GET_PROVIDER_RECEIPT_MESSAGE_ID)
