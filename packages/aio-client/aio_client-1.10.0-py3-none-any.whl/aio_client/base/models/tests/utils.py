# coding: utf-8
from aio_client.base import RequestLog


def mock_request_not_error(result):
    """Мок положительного выполнения запроса к АИО
    :param result: результат, котрый должен вернуть вызов side_effect
    :return: ссылку на функцию side_effect
    """
    def side_effect(log):
        log.state = RequestLog.SENT
        log.save()
        return result
    return side_effect


def mock_request_return_log():
    """Мок выполнения запроса к АИО
    :return: RequestLog
    """
    def side_effect(log):
        log.state = RequestLog.SENT
        log.save()
        return log
    return side_effect
