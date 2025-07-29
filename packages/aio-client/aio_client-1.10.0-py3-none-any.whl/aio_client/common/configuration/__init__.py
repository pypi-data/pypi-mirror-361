# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from abc import ABCMeta
from abc import abstractmethod
from importlib import import_module

# todo: удалить после переноса конфигурации в проекты (deprecated)
# ----------------------------------------------------------------------------
# Изменен способ кастомизации aio_client
# Теперь необходимо объявлять пути к объектам РИС в самой РИС
# в виде экземпляра ClassAttribute или DjangoModelAttribute.
from django.apps import apps
from django.conf import settings
from six import string_types
from six import with_metaclass


class BaseAttribute(with_metaclass(ABCMeta, object)):
    """Базовый класс атрибута конфигурации."""

    def __init__(self, init_data):
        """Создает экземпляр атрибута конфигурации.

        :param init_data: данные для инициализации атрибута.
        """
        self._init_data = init_data
        self._value = None

    @abstractmethod
    def _init_attribute(self):
        """Инициализрует атрибут по указанным данным."""

    def get_value(self):
        """Возвращает инициализированное значение атрибута.

        Применяется для устранения проблемы загрузки Django-моделей при
        старте проекта.
        """
        if not self._value:
            self._value = self._init_attribute()

        return self._value


class ClassAttribute(BaseAttribute):
    """Атрибут, представляющий класс из приложения пользователя."""

    def _init_attribute(self):
        assert isinstance(self._init_data, string_types)
        module_path, cls_name = self._init_data.rsplit('.', 1)
        module_obj = import_module(module_path)
        cls_obj = getattr(module_obj, cls_name)
        return cls_obj


class DjangoModelAttribute(BaseAttribute):
    """Атрибут, представляющий Django-модель приложения пользователя."""

    def _init_attribute(self):
        assert isinstance(self._init_data, string_types)
        model = apps.get_model(self._init_data)
        return model


class ProductConfiguration(object):

    """Класс конфигурации.

    Предоставляет объекты из приложения пользователя.
    Пример использования:
    
    .. code-block:: python

       product_configuration = ProductConfiguration(
           log_model=DjangoModelAttribute('app.Model'),
           task_class=ClassAttribute('celery.task.Task')
       )
    """

    def __init__(self, log_model, task_class):
        assert isinstance(log_model, BaseAttribute)
        assert isinstance(task_class, BaseAttribute)

        self.log_model = log_model
        self.task_class = task_class

    def __getattribute__(self, item):
        attr = super(ProductConfiguration, self).__getattribute__(item)
        if isinstance(attr, BaseAttribute):
            return attr.get_value()
        raise AttributeError

# : Конфигурация ProductConfiguration.
# :
# : В этой переменной должен быть сохранен экземпляр потомка класса
#   `:class: aio_client.common.configuration.ProductConfiguration`.
product_configuration = None

if hasattr(settings, 'SYSTEM_NAME'):
    from yadic import Container
    from aio_client.common.configuration.configuration import (
        ioc_config
    )

    container = Container(ioc_config)
# ----------------------------------------------------------------------------


def get_object(name):
    u"""Возвращает требуемый объект, используя конфигурацию РИС.

    :param string name: Имя объекта из РИС.
    :return: Объект из РИС.
    """
    if isinstance(product_configuration, ProductConfiguration):
        return getattr(product_configuration, name)
    if hasattr(settings, 'SYSTEM_NAME'):
        return container.get(name, settings.SYSTEM_NAME)
    raise AssertionError("AIO-client is not configured")
