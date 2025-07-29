# coding: utf-8
import datetime

from celery import states

from aio_client import configs as aio_client_settings
from aio_client.base import RequestTypeEnum
from aio_client.base.helpers import get_not_sent_post_list
from aio_client.base.tasks import BaseGetAllMessagesTask
from aio_client.base.tasks import TaskContextManager
from aio_client.consumer.helpers import consumer_get_receipt
from aio_client.consumer.helpers import consumer_get_requests
from aio_client.consumer.helpers import consumer_post_request

from .models import PostConsumerRequest


class GetAllReceiptsConsumerTask(BaseGetAllMessagesTask):
    """Задача на получение ответа от СМЭВ по всем отправленным заявкам.

    По каждой заявке отправляем запрос на удаление полученных ответов из AIO.
    """

    description = (u"AIO клиент потребитель. "
                   u"Получение ответа СМЭВ по всем отправленным заявкам.")
    abstract = not aio_client_settings.CONSUMER_ON

    if aio_client_settings.CONSUMER_ON:
        run_every = aio_client_settings.CS_REC_TASK_RUN_EVERY
    else:
        run_every = None

    DELETE_MSG = u'Отправка запроса на удаление полученных ответов от СМЭВ'

    def run(self, *args, **kwargs):
        super(GetAllReceiptsConsumerTask, self).run(*args, **kwargs)
        values = {
            u"Время начала": datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT),
        }
        self.set_progress(
            progress=u"Получение ответа СМЭВ по всем отправленным заявкам...",
            values=values
        )
        messages = []
        title = 'При получении ответов произошла ошибка'
        with TaskContextManager(values, title):
            messages = consumer_get_receipt(values, title)

        values[u'Кол-во сообщений'] = str(len(messages))

        # Удаление в АИО полученных ответов от СМЭВ
        self.delete_messages(messages, values, RequestTypeEnum.CS_DEL_R)

        values[u"Время окончания"] = datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT)
        self.set_progress(
            progress=u'Завершено',
            task_state=states.SUCCESS,
            values=values)

        return self.state


class GetAllResponsesConsumerTask(BaseGetAllMessagesTask):
    """Задача на получение всех ответов из очереди СМЭВ.

    По каждому ответу отправляем запрос на его удаление из AIO.
    """

    description = (u"AIO клиент потребитель. "
                   u"Получение всех ответов из очереди СМЭВ.")
    abstract = not aio_client_settings.CONSUMER_ON

    if aio_client_settings.CONSUMER_ON:
        run_every = aio_client_settings.CS_RES_TASK_RUN_EVERY
    else:
        run_every = None

    DELETE_MSG = (
        u'Отправка запроса на удаление полученного ответа от СМЭВ в АИО')
    DELETE_ERR_MSG = (
        u'Не удалось отправить запрос на удаление полученного '
        u'ответа от СМЭВ')

    def run(self, *args, **kwargs):
        super(GetAllResponsesConsumerTask, self).run(*args, **kwargs)
        values = {
            u"Время начала": datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT),
        }
        self.set_progress(
            progress=u"Получаем ответа СМЭВ по всем отправленным заявкам ...",
            values=values)

        messages = []
        title = 'При получении ответа СМЭВ произошла ошибка'
        with TaskContextManager(values, title):
            messages = consumer_get_requests(values, title)

        values[u'Кол-во ответов'] = str(len(messages))

        # Удаление в АИО полученных ответов от СМЭВ
        self.delete_messages(messages, values, RequestTypeEnum.CS_DEL)

        # проверка наличия сообщений пост на повторную отправку
        not_sent_post_list = get_not_sent_post_list(PostConsumerRequest)
        if not_sent_post_list:
            values[u'Найдено %d заявок РИС на повторную отправку'
                   % len(not_sent_post_list)] = u''
            for request_msg in not_sent_post_list:
                consumer_post_request(request_msg)

        values[u"Время окончания"] = datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT)
        self.set_progress(
            progress=u'Завершено',
            task_state=states.SUCCESS,
            values=values)

        return self.state
