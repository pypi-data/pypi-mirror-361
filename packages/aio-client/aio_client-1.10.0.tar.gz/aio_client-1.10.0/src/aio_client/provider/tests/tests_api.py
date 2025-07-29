# coding: utf-8
import json

from django.test import TestCase
from requests import HTTPError
import six

from aio_client.base import RequestTypeEnum
from aio_client.base.models.tests.utils import mock_request_not_error
from aio_client.provider.api import get_requests_by_message_types
from aio_client.provider.api import get_response
from aio_client.provider.exceptions import ReceiptNotFound
from aio_client.provider.exceptions import ResponseNotFound
from aio_client.provider.helpers import _prepare_log
from aio_client.provider.models import GetProviderRequest
from aio_client.provider.models.tests.factory_provider import \
    PostProviderRequestF
import aio_client

from .request_data import TEST_GET_PROVIDER_RECEIPT_EXAMPLE
from .request_data import TEST_GET_PROVIDER_RECEIPT_MESSAGE_ID
from .request_data import TEST_GET_PROVIDER_REQUEST_EXAMPLE
from .request_data import TEST_GET_PROVIDER_REQUEST_MESSAGE_ID
from .request_data import TEST_GET_PROVIDER_REQUEST_MESSAGE_TYPE


if six.PY2:
    import mock
else:
    from unittest import mock


class ApiTestCase(TestCase):

    def setUp(self):
        self.request_type = RequestTypeEnum.PR_GET
        self.request_log = _prepare_log(self.request_type)

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_get_requests(self, sender):
        """Вызываем хелпер получения запросв к РИС, проверяем что апи функция
        их отдает и помечает как обработанные"""

        mock_resp = json.loads(TEST_GET_PROVIDER_REQUEST_EXAMPLE)
        return_value = mock.Mock(ok=True)
        return_value.json.return_value = mock_resp
        sender.side_effect = mock_request_not_error(return_value)
        # эмуляция вызова в GetAllRequestsProvideTask получения запросов к РИС
        aio_client.provider.helpers.provider_get_requests()

        self.assertEqual(
            GetProviderRequest.objects.filter(
                state=GetProviderRequest.NOT_SENT).count(), 1)
        # вызов тестируемой функции получения запросов
        result = get_requests_by_message_types(message_types=TEST_GET_PROVIDER_REQUEST_MESSAGE_TYPE)
        self.assertEqual(len(result), 1)

        self.assertEqual(GetProviderRequest.objects.filter(
                state=GetProviderRequest.SENT).count(), 1)

        # заявка из файла GetProviderRequest.json
        self.assertEqual(result[0]['message_id'],
                         TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_get_response_not_found(self, sender):
        """Запрос ответа по заявке, ответ на которую мы не отправляли вызывает
        """
        with self.assertRaises(ResponseNotFound):
            get_response(TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)

    def test_get_response_receipt_not_found(self):
        """Запрос ответа по заявке, квитанцию еще не получили вызывает
        ReceiptNotFound"""
        # отправляем ответ на заявку
        request_msg = PostProviderRequestF(
            origin_message_id=TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)
        with mock.patch('aio_client.base.helpers.send_request') as sender:
            sender.side_effect = mock_request_not_error(
                mock.Mock(status_code=201))
            aio_client.provider.helpers.provider_post_request(request_msg)

        with mock.patch('aio_client.provider.helpers.send_request'):
            # запрос ответа по заявке, квитанцию еще не получили
            with self.assertRaises(ReceiptNotFound):
                get_response(TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)

    def test_get_response(self):
        # отправляем ответ на заявку
        request_msg = PostProviderRequestF(
            origin_message_id=TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)
        with mock.patch('aio_client.base.helpers.send_request') as sender:
            sender.side_effect = mock_request_not_error(
                mock.Mock(status_code=201))
            aio_client.provider.helpers.provider_post_request(request_msg)

        # запрашиваем квитанцию
        mock_resp = json.loads(TEST_GET_PROVIDER_RECEIPT_EXAMPLE)
        with mock.patch('aio_client.provider.helpers.send_request') as sender:
            return_value = mock.Mock(ok=True)
            return_value.json.return_value = mock_resp
            sender.side_effect = mock_request_not_error(return_value)
            aio_client.provider.helpers.provider_get_receipt()

        result = get_response(TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)
        self.assertEqual(result['origin_message_id'],
                         TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_delete_request(self, sender):
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=204))
        response = aio_client.base.helpers.delete_messages(
            RequestTypeEnum.PR_DEL,
            TEST_GET_PROVIDER_REQUEST_MESSAGE_ID)
        self.assertEqual(response.status_code, 204)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_delete_request_not_exists(self, sender):
        mock_resp = mock.Mock(
            status_code=404, raise_for_status=HTTPError("Not Found"))
        sender.side_effect = mock_request_not_error(mock_resp)
        response = aio_client.base.helpers.delete_messages(
            RequestTypeEnum.PR_DEL, '0')
        self.assertEqual(response.status_code, 404)

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_delete_receipt(self, sender):
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=204))
        response = aio_client.base.helpers.delete_messages(
            RequestTypeEnum.PR_DEL_R,
            TEST_GET_PROVIDER_RECEIPT_MESSAGE_ID)
        self.assertEqual(response.status_code, 204)
