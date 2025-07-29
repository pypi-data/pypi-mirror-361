# coding: utf-8

from celery.schedules import maybe_schedule

from aio_client.base.exceptions import AioClientException
from aio_client.base.helpers import delete_messages
from aio_client.common.configuration import get_object


# Класс асинхронной задачи
AsyncTask = get_object("task_class")


class TaskContextManager:
    """Контекст менеджер для обработки исключений при работе тасков"""

    def __init__(self, values, title):
        self.values = values
        self.title = title

    def __enter__(self):
        """"""

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and issubclass(exc_type, AioClientException):
            self.values[self.title] = u'%s (код ошибки - %s)' % (
                exc_value.message, exc_value.code)
            return True


class PeriodicAsyncTask(AsyncTask):
    """Периодическая задача - это задача, которая добавляет себя в
     настройку: setting: `CELERYBEAT_SCHEDULE`"""
    abstract = True
    ignore_result = True
    relative = False
    options = None
    compat = True

    def __init__(self):
        if not hasattr(self, 'run_every'):
            raise NotImplementedError(
                'Periodic tasks must have a run_every attribute')
        self.run_every = maybe_schedule(self.run_every, self.relative)
        super(PeriodicAsyncTask, self).__init__()

    @classmethod
    def on_bound(cls, app):
        app.conf.CELERYBEAT_SCHEDULE[cls.name] = {
            'task': cls.name,
            'schedule': cls.run_every,
            'args': (),
            'kwargs': {},
            'options': cls.options or {},
            'relative': cls.relative,
        }


class BaseGetAllMessagesTask(PeriodicAsyncTask):
    """Задача на получение всех сообщений из АИО.

    Содержит методы для удаления полученных сообщений.
    """
    abstract = True

    stop_executing = False
    LOG_TIME_FORMAT = "%d.%m.%Y %H:%M"

    # Кол-во удаляемых сообщений за один запрос
    BULK_DELETE_SIZE = 20

    DELETE_MSG = u'Отправка запроса на удаление в АИО'
    DELETE_ERR_MSG = u'Не удалось отправить запрос на удаление сообщений'

    def delete_messages(self, messages, values, request_type):
        """Удаление полученных сообщений в АИО.

        :param messages: Список плученных из АИО сообщений
        :type messages: list[dict]
        :param values: Словарь с результатами выполнения задачи
        :type values: dict
        :param request_type: Тип запроса на удаление
        :type request_type: RequestTypeEnum
        """
        message_ids = []
        for num, message in enumerate(messages, 1):
            message_id = message.get('message_id')
            values[u'Сообщение %s' % message_id] = self.DELETE_MSG
            message_ids.append(message_id)

            if not self.BULK_DELETE_SIZE or num % self.BULK_DELETE_SIZE == 0:
                self.send_delete_request(
                    message_ids, values, request_type, self.DELETE_ERR_MSG
                )
                message_ids = []
        else:
            if message_ids:
                # Если ещё остались сообщения для удаления
                self.send_delete_request(
                    message_ids, values, request_type, self.DELETE_ERR_MSG
                )

    @staticmethod
    def send_delete_request(message_ids, values, request_type, err_msg=''):
        """Отправка запроса на удаление полученных заявок.

        :param message_ids: id сообщений
        :type message_ids: str or list[str]
        :param values: Словарь с результатами выполнения задачи
        :type values: dict
        :param request_type: Тип запроса на удаление
        :type request_type: RequestTypeEnum
        :param err_msg: Текст сообщения об ошибке выполнения запроса
        :type err_msg: basestring
        """
        err_message = u'%s: %s' % (err_msg, ', '.join(message_ids))
        with TaskContextManager(values, err_message):
            delete_messages(request_type, *message_ids)
