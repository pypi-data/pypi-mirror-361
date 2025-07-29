# coding: utf-8
import json

from django.test import TestCase
from requests.exceptions import HTTPError
import six

from aio_client.base import RequestTypeEnum
from aio_client.base.helpers import _prepare_log
from aio_client.base.models.tests.utils import mock_request_not_error
from aio_client.consumer.models import GetConsumerReceipt
from aio_client.consumer.models import GetConsumerResponse
from aio_client.consumer.models import PostConsumerRequest
import aio_client

from .request_data import TEST_GET_CONSUMER_RECEIPT_EXAMPLE
from .request_data import TEST_GET_CONSUMER_RECEIPT_MESSAGE_ID
from .request_data import TEST_GET_CONSUMER_REQUEST_EXAMPLE
from .request_data import TEST_GET_CONSUMER_REQUEST_MESSAGE_ID
from .request_data import TEST_GET_CONSUMER_REQUEST_OR_MESSAGE_ID
from .request_data import TEST_POST_CONSUMER_REQUEST_MESSAGE_ID


if six.PY2:
    import mock
else:
    from unittest import mock


class HelpersTestCase(TestCase):

    def setUp(self):
        self.request_type = RequestTypeEnum.CS_POST
        self.request_log = _prepare_log(self.request_type)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_consumer_post_request(self, sender):
        """Проверка что запрос успешно ушел и попал в БД"""
        request_msg = PostConsumerRequest(
            message_id=TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=200))
        response = aio_client.consumer.helpers.consumer_post_request(
            request_msg)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PostConsumerRequest.objects.all().count(), 1)
        self.assertEqual(
            PostConsumerRequest.objects.all()[0].message_id,
            TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)

    @mock.patch('aio_client.consumer.helpers.send_request')
    def test_consumer_get_receipt(self, sender):
        """Проверка что запрос успешно ушел и попал в БД"""
        mock_resp = json.loads(TEST_GET_CONSUMER_RECEIPT_EXAMPLE)
        return_value = mock.Mock(ok=True)
        return_value.json.return_value = mock_resp
        sender.side_effect = mock_request_not_error(return_value)
        response = aio_client.consumer.helpers.consumer_get_receipt()
        # в ответе 1 заявка
        self.assertEqual(len(response), 1)
        # в таблице 1 заявка
        self.assertEqual(GetConsumerReceipt.objects.all().count(), 1)
        self.assertEqual(response[0]['message_id'],
                         TEST_GET_CONSUMER_RECEIPT_MESSAGE_ID)

    @mock.patch('aio_client.consumer.helpers.send_request')
    def test_consumer_get_requests(self, sender):
        """Если ответ не пуст, то сообщение должно попасть в БД"""
        mock_resp = json.loads(TEST_GET_CONSUMER_REQUEST_EXAMPLE)
        return_value = mock.Mock(ok=True)
        return_value.json.return_value = mock_resp
        sender.side_effect = mock_request_not_error(return_value)

        response = aio_client.consumer.helpers.consumer_get_requests()
        # в ответе 1 заявка
        self.assertEqual(len(response), 1)
        # в таблице 1 заявка
        self.assertEqual(GetConsumerResponse.objects.all().count(), 1)

        self.assertEqual(response[0]['origin_message_id'],
                         TEST_GET_CONSUMER_REQUEST_OR_MESSAGE_ID)

    @mock.patch('aio_client.consumer.helpers.send_request')
    def test_consumer_delete_request_not_exists(self, sender):
        mock_resp = mock.Mock(
            status_code=404, raise_for_status=HTTPError("Not Found"))
        sender.side_effect = mock_request_not_error(mock_resp)
        response = aio_client.consumer.helpers.consumer_delete_request('0')
        self.assertEqual(response.status_code, 404)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_consumer_post_request_new_message_id(self, sender):
        """При повторном формировании запросов от потребителя следует
         присваивать им новый message_id"""
        request_msg = PostConsumerRequest(
            message_id=TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=405))
        response = aio_client.consumer.helpers.consumer_post_request(
            request_msg)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(PostConsumerRequest.objects.all().count(), 1)
        self.assertEqual(
            PostConsumerRequest.objects.all()[0].message_id,
            TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
        # повторно отправляем, проверяем что идентификатор именился
        aio_client.consumer.helpers.consumer_post_request(
            request_msg)
        self.assertNotEqual(
            PostConsumerRequest.objects.all()[0].message_id,
            TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
