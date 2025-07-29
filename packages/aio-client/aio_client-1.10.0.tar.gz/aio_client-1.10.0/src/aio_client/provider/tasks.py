# coding: utf-8
import datetime

from celery import states

from aio_client import configs as aio_client_settings
from aio_client.base import RequestTypeEnum
from aio_client.base.helpers import get_not_sent_post_list
from aio_client.base.tasks import BaseGetAllMessagesTask
from aio_client.base.tasks import TaskContextManager
from aio_client.provider.helpers import provider_get_receipt
from aio_client.provider.helpers import provider_get_requests
from aio_client.provider.helpers import provider_post_request

from .models import PostProviderRequest


class GetAllRequestsProvideTask(BaseGetAllMessagesTask):
    """Задача на получение всех заявок к РИС от СМЭВ.

    Каждую заявку сохраняет в БД и отправляет запрос на удаление
    полученных заявок из AIO.
    """

    description = (u"AIO клиент поставщик. Получение всех заявок к РИС."
                   u" Отправка ответов.")
    abstract = not aio_client_settings.PROVIDER_ON

    if aio_client_settings.PROVIDER_ON:
        run_every = aio_client_settings.PR_REQ_TASK_RUN_EVERY
    else:
        run_every = None

    def run(self, *args, **kwargs):
        super(GetAllRequestsProvideTask, self).run(*args, **kwargs)
        values = {
            u"Время начала": datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT),
        }
        self.set_progress(
            progress=u"Получаем все заявки к РИС в качестве поставщика ...",
            values=values
        )
        messages = []
        title = 'При получении заявок произошла ошибка'
        with TaskContextManager(values, title):
            messages = provider_get_requests(values, title)

        values[u'Кол-во сообщений'] = str(len(messages))

        # Удаление полученных заявок в АИО
        self.delete_messages(messages, values, RequestTypeEnum.PR_DEL)

        # проверка наличия сообщений пост на повторную отправку
        not_sent_post_list = get_not_sent_post_list(PostProviderRequest)
        if not_sent_post_list:
            values[u'Найдено %d ответов РИС на повторную отправку'
                   % len(not_sent_post_list)] = u''
            for request_msg in not_sent_post_list:
                provider_post_request(request_msg)

        self.set_progress(
            progress=u"Получаем все заявки к РИС в качестве поставщика ...",
            values=values
        )

        values[u"Время окончания"] = datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT)

        self.set_progress(
            progress=u'Завершено',
            task_state=states.SUCCESS,
            values=values)

        return self.state


class GetAllReceiptsProvideTask(BaseGetAllMessagesTask):
    """Задача на получение ответа СМЭВ по всем отправленным заявкам.

    По каждому ответу отправляем запрос на его удаление из AIO.
    """

    description = (u"AIO клиент поставщик."
                   u" Получение ответа СМЭВ по всем отправленным заявкам.")
    abstract = not aio_client_settings.PROVIDER_ON

    if aio_client_settings.PROVIDER_ON:
        run_every = aio_client_settings.PR_REC_TASK_RUN_EVERY
    else:
        run_every = None

    DELETE_MSG = (
        u'Отправка запроса на удаление полученной квитанции от СМЭВ в АИО')
    DELETE_ERR_MSG = (
        u'Не удалось отправить запрос на удаление полученной'
        u' квитанции от СМЭВ')

    def run(self, *args, **kwargs):
        super(GetAllReceiptsProvideTask, self).run(*args, **kwargs)
        values = {
            u"Время начала": datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT),
        }
        self.set_progress(
            progress=u"Получение ответа СМЭВ по всем отправленным заявкам ...",
            values=values
        )
        messages = []
        title = 'При получении ответов произошла ошибка'
        with TaskContextManager(values, title):
            messages = provider_get_receipt(values, title)

        values[u'Кол-во квитанций'] = str(len(messages))

        # Удаление в АИО полученных квитанций
        self.delete_messages(messages, values, RequestTypeEnum.PR_DEL_R)

        values[u"Время окончания"] = datetime.datetime.now(
            ).strftime(self.LOG_TIME_FORMAT)
        self.set_progress(
            progress=u'Завершено',
            task_state=states.SUCCESS,
            values=values)

        return self.state
