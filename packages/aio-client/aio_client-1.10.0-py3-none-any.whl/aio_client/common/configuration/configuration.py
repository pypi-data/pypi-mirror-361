# coding: utf-8

from __future__ import absolute_import

import os


def get_option(config=None, key=None):
    return getattr(config, key)


# точное наименование модуля настроек
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')


def option_full_name(option):
    # получение полного имени настройки
    return "%s.%s" % (settings_module, option)


# Базовые примитивы и параметры конфигурации специфичные для ИС
ioc_config = {
    # Модель логирования СМЭВ запросов
    "log_model": {
        "__default__": {
            "__type__": "static"
        },
        "kinder": {
            "__realization__": "educommon.ws_log.models.SmevLog"
        },
        "web_edu": {
            "__realization__": "educommon.ws_log.models.SmevLog"
        },
        "ssuz": {
            "__realization__": "educommon.ws_log.models.SmevLog"
        },
        "eduadnl": {
            "__realization__": "extedu.ws_logs.utils.LogAdapter"
        }
    },
    # Базовый класс логирующей асинхронной задачи
    "task_class": {
        "__default__": {
            "__type__": "static",
        },
        "kinder": {
            "__realization__": "kinder.core.async_tasks.tasks.AsyncTask"
        },
        "web_edu": {
            "__realization__": "web_edu.core.async_task.tasks.AsyncTask"
        },
        "ssuz": {
            "__realization__": "ssuz.async_tasks.tasks.AsyncTask"
        },
        "eduadnl": {
            "__realization__": "educommon.async.tasks.AsyncTask"
        }
    },
}
