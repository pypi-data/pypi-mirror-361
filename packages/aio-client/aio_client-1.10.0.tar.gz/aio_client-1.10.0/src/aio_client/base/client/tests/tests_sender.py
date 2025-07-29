# coding: utf-8
from django.test import TestCase
from requests import ConnectionError  # pylint: disable=redefined-builtin
from requests import HTTPError
from requests import Timeout
from requests import TooManyRedirects
import six

from aio_client.base import RequestLog
from aio_client.base import RequestTypeEnum
from aio_client.base import _prepare_log
from aio_client.base.client.sender import POST_CREATE_CODE
from aio_client.base.client.sender import send_request
from aio_client.base.exceptions import HttpErrorException
from aio_client.base.exceptions import HttpFailureException
from aio_client.base.exceptions import TransportException


if six.PY2:
    import mock
else:
    from unittest import mock


class SenderTestCase(TestCase):

    def setUp(self):
        self.request_type = RequestTypeEnum.PR_GET
        self.request_log = _prepare_log(self.request_type)

    def _check_result(self, exc, error, state):
        with self.assertRaises(exc):
            send_request(self.request_log)
        self.assertIsNot(self.request_log.error, error)
        self.assertEqual(self.request_log.state, state)

    @mock.patch('requests.request')
    def tests_transport_error(self, func):
        """Ошибки вида ConnectionError, Timeout, TooManyRedirects
        должны генерить TransportException, статус отправки остается NOT_SENT
        """
        param = (TransportException, '', RequestLog.NOT_SENT)

        func.side_effect = ConnectionError()
        self._check_result(*param)

        func.side_effect = Timeout()
        self._check_result(*param)

        func.side_effect = TooManyRedirects()
        self._check_result(*param)

    @mock.patch('requests.request')
    def tests_http_error(self, func):
        """Ошибки вида HttpError, должны генерить HttpErrorException
        статус отправки ERROR
        """
        func.side_effect = HTTPError()
        self._check_result(HttpErrorException, '', RequestLog.ERROR)

    @mock.patch('requests.request', autospec=True)
    def tests_status_code(self, func):
        """Если запрос ушел успешно, меняет статус на SENT
        Если код в ответе из списка HTTP_FAILURE_CODES, то меняем статус на SENT.
        и заполяем поле error В модели запроса.
        Если пост запрос вернул код не 201, генерим ошибку,
        статус сообщения SENT
        """
        func.return_value = mock.Mock(status_code=200)
        send_request(self.request_log)
        self.assertEqual(self.request_log.error, '')
        self.assertEqual(self.request_log.state, RequestLog.SENT)

        func.return_value = mock.Mock(status_code=405)
        self._check_result(HttpFailureException, '405', RequestLog.SENT)

        self.request_type = RequestTypeEnum.PR_POST
        self.request_log = _prepare_log(self.request_type)

        func.return_value = mock.Mock(status_code=POST_CREATE_CODE)
        send_request(self.request_log)
        self.assertEqual(self.request_log.error, '')
        self.assertEqual(self.request_log.state, RequestLog.SENT)

        func.return_value = mock.Mock(status_code=200)
        self._check_result(HttpFailureException, '200', RequestLog.SENT)
