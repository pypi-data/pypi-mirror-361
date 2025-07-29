# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery.schedules import crontab
from django.conf import settings as dj_settings
from django.core.exceptions import ImproperlyConfigured
import yaml


_CRONTAB = 'crontab'
_TIMEDELTA = 'timedelta'
_AVAILABLE_SCHEDULE_TYPES = (_CRONTAB, _TIMEDELTA)


def __create_schedule(schedule_type, **kwargs):
    """Создает расписание для периодических задач в зависимости от типа."""
    if schedule_type not in _AVAILABLE_SCHEDULE_TYPES:
        raise ImproperlyConfigured(
            'Некорректный тип расписания. '
            'Допустимые типы: {}'.format(', '.join(_AVAILABLE_SCHEDULE_TYPES))
        )
    error_msg = 'Для типа расписания {} обязательные параметры {}'
    if schedule_type == _CRONTAB:
        minute = kwargs.get('min')
        hour = kwargs.get('hour')
        if not all((minute, hour)):
            raise ImproperlyConfigured(
                error_msg.format(
                    schedule_type, ', '.join(('min', 'hour'))
                )
            )
        result = crontab(minute=minute, hour=hour)
    else:
        result = kwargs.get('second')
        if not result:
            raise ImproperlyConfigured(
                error_msg.format(schedule_type, 'second')
            )
        if not isinstance(result, (int, float)):
            raise ImproperlyConfigured(
                'Атрибут {} должен быть числом.'.format('second')
            )

    return result


# Общие настройки
AIO_CLIENT_CONFIG_FILE_NAME = 'aio_client.yaml'

# переменная пути к конфигам может быть разной в разных проектах
if hasattr(dj_settings, '_CONFIG_PATH'):
    config_path = dj_settings._CONFIG_PATH
elif hasattr(dj_settings, 'CONFIG_PATH'):
    config_path = dj_settings.CONFIG_PATH
else:
    raise ValueError('Variable CONFIG_PATH is not found')


AIO_CLIENT_CONFIG = os.path.join(config_path, AIO_CLIENT_CONFIG_FILE_NAME)

cfg = yaml.load(open(AIO_CLIENT_CONFIG), yaml.loader.SafeLoader)
# Адрес сервера AIO
AIO_SERVER = cfg['common']['server']
# данные для аутентификации на сервере АИО
USER = cfg['common']['user']
PASSWORD = cfg['common']['password']
DEBUG_MODE = bool(cfg['common']['debugmode'])
# Таймаут при отправке запроса в АИО
REQUEST_TIMEOUT_SEC = int(
    cfg['common'].get('request_timeout_sec', 1)
)
PROVIDER_ON = bool(cfg['provider'])
CONSUMER_ON = bool(cfg['consumer'])

# Время, спустя которое неотправленному
# сообщению присваивается статус ошибки
# по умолчанию 1 день.
EXPIRY_DATE = cfg['common'].get('expiry_date', 1)

# настройки запуска таска "AIO клиент провайдер. Получение всех заявок к РИС."
_PROVIDER_REQ_CELERY = cfg['celery']['provider']['request']
PR_REQ_TASK_RUN_EVERY = __create_schedule(
    _PROVIDER_REQ_CELERY['type'],
    **_PROVIDER_REQ_CELERY['run_every']
)
# настройки запуска таска "AIO клиент провайдер.
# Получение ответа СМЭВ по всем отправленным заявкам."
_PROVIDER_REC_CELERY = cfg['celery']['provider']['receipt']
PR_REC_TASK_RUN_EVERY = __create_schedule(
    _PROVIDER_REC_CELERY['type'],
    **_PROVIDER_REC_CELERY['run_every']
)
# настройки запуска таска "AIO клиент поставщик.
# Получение всех ответов из очереди СМЭВ"
_CS_RES_CELERY = cfg['celery']['consumer']['response']
CS_RES_TASK_RUN_EVERY = __create_schedule(
    _CS_RES_CELERY['type'],
    **_CS_RES_CELERY['run_every']
)
# настройки запуска таска "AIO клиент поставщик.
# Получение ответа СМЭВ по всем отправленным заявкам."
_CS_REC_CELERY = cfg['celery']['consumer']['receipt']
CS_REC_TASK_RUN_EVERY = __create_schedule(
    _CS_REC_CELERY['type'],
    **_CS_REC_CELERY['run_every']
)
