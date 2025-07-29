# coding: utf-8
import json

from django.test import TestCase
from requests import HTTPError
import six

from aio_client.base import RequestTypeEnum
from aio_client.base.models.tests.utils import mock_request_not_error
from aio_client.consumer.api import get_response
from aio_client.consumer.api import push_request
from aio_client.consumer.exceptions import RequestNotFound
from aio_client.consumer.helpers import _prepare_log
from aio_client.consumer.models import PostConsumerRequest
import aio_client

from .request_data import TEST_GET_CONSUMER_RECEIPT_MESSAGE_ID
from .request_data import TEST_GET_CONSUMER_REQUEST_EXAMPLE
from .request_data import TEST_GET_CONSUMER_REQUEST_MESSAGE_ID
from .request_data import TEST_GET_CONSUMER_REQUEST_OR_MESSAGE_ID
from .request_data import TEST_POST_CONSUMER_REQUEST_MESSAGE_ID


if six.PY2:
    import mock
else:
    from unittest import mock


class ApiTestCase(TestCase):

    def setUp(self):
        self.request_type = RequestTypeEnum.PR_GET
        self.request_log = _prepare_log(self.request_type)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_push_request(self, sender):
        # отправляем заявку
        request_msg = PostConsumerRequest(
            message_id=TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=200))
        push_request(request_msg)
        self.assertEqual(PostConsumerRequest.objects.all().count(), 1)
        self.assertEqual(
            PostConsumerRequest.objects.all()[0].message_id,
            TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)

    @mock.patch('aio_client.consumer.helpers.send_request')
    def test_get_response_not_found(self, sender):
        """Запрос ответа по заявке, ответ на которую мы не отправляли вызывает
        RequestNotFound
        """
        with self.assertRaises(RequestNotFound):
            get_response(TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)

    def test_get_response_response_not_found(self):
        """Запрос ответа по заявке, ответа еще не получили, возращает None"""
        # отправляем заявку
        request_msg = PostConsumerRequest(
            message_id=TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
        with mock.patch('aio_client.base.helpers.send_request') as sender:
            sender.side_effect = mock_request_not_error(
                mock.Mock(status_code=201))
            push_request(request_msg)
        with mock.patch('aio_client.consumer.helpers.send_request') as sender:
            # запрос ответа по заявке, ответа еще не получили
            self.assertEqual(
                get_response(TEST_POST_CONSUMER_REQUEST_MESSAGE_ID), None)

    def test_get_response(self):
        """Запрос ответа по заявке"""
        # отправляем заявку
        request_msg = PostConsumerRequest(
            message_id=TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
        with mock.patch('aio_client.base.helpers.send_request') as sender:
            sender.side_effect = mock_request_not_error(
                mock.Mock(status_code=201))
            push_request(request_msg)
        with mock.patch('aio_client.consumer.helpers.send_request') as sender:
            mock_resp = json.loads(TEST_GET_CONSUMER_REQUEST_EXAMPLE)
            return_value = mock.Mock(ok=True)
            return_value.json.return_value = mock_resp
            sender.side_effect = mock_request_not_error(return_value)
            # эмуляция работы таска GetAllResponsesConsumerTask
            # запрашиваем ответы
            aio_client.consumer.helpers.consumer_get_requests()
            result = get_response(TEST_POST_CONSUMER_REQUEST_MESSAGE_ID)
            self.assertEqual(result['origin_message_id'],
                             TEST_GET_CONSUMER_REQUEST_OR_MESSAGE_ID)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_delete_request(self, sender):
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=204))
        response = aio_client.base.helpers.delete_messages(
            RequestTypeEnum.CS_DEL,
            TEST_GET_CONSUMER_REQUEST_MESSAGE_ID)
        self.assertEqual(response.status_code, 204)

    @mock.patch('aio_client.base.helpers.send_request')
    def test_delete_request_not_exists(self, sender):
        mock_resp = mock.Mock(
            status_code=404, raise_for_status=HTTPError("Not Found"))
        sender.side_effect = mock_request_not_error(mock_resp)
        response = aio_client.base.helpers.delete_messages(
            RequestTypeEnum.CS_DEL, '0')
        self.assertEqual(response.status_code, 404)

    @mock.patch('aio_client.provider.helpers.send_request')
    def test_delete_receipt(self, sender):
        sender.side_effect = mock_request_not_error(mock.Mock(status_code=204))
        response = aio_client.base.helpers.delete_messages(
            RequestTypeEnum.CS_DEL_R,
            TEST_GET_CONSUMER_RECEIPT_MESSAGE_ID)
        self.assertEqual(response.status_code, 204)
