# coding: utf-8
import functools

from aio_client.configs import DEBUG_MODE
import django.dispatch


# Сигнал - получение всех данных завершено
get_data_done = django.dispatch.Signal()


def robust_sender(signal, **kwargs):
    """
    Декоратор отправки сигнала методом send_robust. Не учитывает
    возможность отправки аргументов сигнала::

        @robust_sender(get_data_done, sender=GetProviderRequest)
        def data_getter():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            result, is_send_signal = func(*a, **kw)
            # Задумка в том, что сигнал отправляется при получении записей с aio-сервера, но, поскольку
            # ряд тестов сервисов происходит с помощью ручного создания записей в админке,
            # отправляем сигнал о новых записях в любом случае, если стоит DEBUG_MODE
            if is_send_signal or DEBUG_MODE:
                signal.send_robust(**kwargs)
            return result
        return wrapper
    return decorator
