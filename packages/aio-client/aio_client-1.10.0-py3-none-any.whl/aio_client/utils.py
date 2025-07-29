# coding: utf-8
from __future__ import absolute_import

from functools import wraps
from uuid import uuid1

import celery
import dateutil.parser


def convert(s):
    """Строку в datetime"""
    return dateutil.parser.parse(s)


def to_str_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return str(result)
    return wrapper


uuid = to_str_decorator(uuid1)


def register_task(task):
    u"""Регистрирует задание в Celery.

    Начиная с Celery 4.x появилась необходимость регистрировать задания,
    основанные на классах с помощью метода
    :meth:`~celery.app.base.Celery.register_task`. В более ранних версиях
    Celery задания регистрируются автоматически.

    :rtype: celery.app.task.Task
    """
    if celery.VERSION < (4, 0, 0):
        return task

    elif celery.VERSION == (4, 0, 0):
        # В Celery 4.0.0 нет метода для регистрации заданий,
        # исправлено в 4.0.1
        raise Exception(u'Use Celery 4.0.1 or later.')

    else:
        app = celery.app.app_or_default()
        return app.register_task(task)
