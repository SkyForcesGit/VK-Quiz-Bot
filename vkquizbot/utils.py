# Package name: vkquizbot
# Module name: utils.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль является вспомогательным и содержит в себе классы и методы общего назначения,
которые используются во всех прочих модулях бота.

Список классов и методов:
| UtilsInitDefault
    Данный класс отвечает за стандартный шаблон инициализации класса.

| UtilsInitVKAPI(UtilsInitDefault)
    Данный класс отвечает за стандартный шаблон инициализации сессии VK API для класса.

| UtilsInitLongpoll(UtilsInitVKAPI)
    Данный класс отвечает за стандартный шаблон инициализации Longpoll API и Bot Longpoll
    API для класса.

| UtilsInitMessage(UtilsInitVKAPI)
    Данный класс отвечает за стандартный шаблон инициализации загрузчика данных VK Uploader
    для класса.

| ErrorNotifier
    Данный класс отвечает за работу различных оповещений об ошибках.

⌊__ create_exception_flag
        Данный метод при возникновении исключения в работе бота создает флаг с информацией
        о возникшем исключении, включая Traceback.

⌊__ remove_previous_flags
        Данный метод удаляет флаги об ошибках с предыдущего сеанса.

⌊__ notify [DECORATOR]
        Данный метод позволяет регистрировать ошибки в других методах и сообщать о них
        администратору бота.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import json
import threading
import traceback
import random
import datetime
import os
from typing import Callable, Any
from functools import wraps

# Сторонние библиотеки
import playsound
import vk_api
from vk_api.longpoll import VkLongPoll
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api import VkUpload

# Модули бота
from .consts import Consts


# pylint: disable=too-few-public-methods
class UtilsInitDefault:
    """
    Данный класс является вспомогательным и отвечает за загрузку файла конфигурации и инициализацию
    локера потоков для всех классов, которые от него наследуются.
    """
    def __init__(self) -> None:
        with open("data/bot_config.json", encoding="utf-8") as bot_config:
            self._bot_config = json.load(bot_config)
        self._locker = threading.RLock()


class UtilsInitVKAPI(UtilsInitDefault):
    """
    Данный класс является вспомогательным и отвечает за инициализацию сессии VK API для всех
    классов, которые от него наследуются.
    """
    def __init__(self) -> None:
        super().__init__()
        self._vk_session = vk_api.VkApi(token=self._bot_config["vk_api_community_access_key"])


class UtilsInitLongpoll(UtilsInitVKAPI):
    """
    Данный класс является вспомогательным и отвечает за инициализацию Longpoll API и Bot Longpoll
    API для всех классов, которые от него наследуются.
    """
    def __init__(self) -> None:
        super().__init__()
        self._longpoll = VkLongPoll(self._vk_session)
        self._bot_longpoll = VkBotLongPoll(self._vk_session, group_id=self._bot_config["group_id"])


class UtilsInitMessage(UtilsInitVKAPI):
    """
    Данный класс является вспомогательным и отвечает за инициализацию загрузчика данных VK Uploader
    для всех классов, которые от него наследуются.
    """
    def __init__(self) -> None:
        super().__init__()
        self._uploader = VkUpload(self._vk_session)


class ErrorNotifier:
    """
    Данный класс отвечает за работу различных оповещений об ошибках.

    Конструктор класса:
    Отсутствует.

    Список публичных методов:
    (class and static methods)
    | create_exception_flag
    | remove_previous_flags
    | notify [DECORATOR]
    """
    with open("data/bot_config.json", encoding="utf-8") as bot_config:
        _bot_config = json.load(bot_config)
    _vk_session = vk_api.VkApi(token=_bot_config["vk_api_community_access_key"])

    @staticmethod
    def create_exception_flag(exc_name: str, exc_traceback: str) -> None:
        """
        Данный статический метод при возникновении исключения в работе бота создает в папке 'dump'
        флаг с информацией о возникшем исключении, включая Traceback. Данные флаги используются для
        работы системы восстановления предыдущего сеанса.

        :param exc_name: имя исключения. Будет использовано в названии файла.
        :param exc_traceback: Traceback. Будет записан в файл.
        :return: ничего (None).
        """
        with open(f"dump/exc_{exc_name}_at_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.flag",
                  mode="w", encoding="utf-8") as flag_write:
            flag_write.write(exc_traceback)

    @staticmethod
    def remove_previous_flags() -> None:
        """
        Данный статический метод удаляет флаги об ошибках с предыдущего сеанса после успешного
        восстановления предыдущего сеанса.

        :return: ничего (None).
        """
        for flag in [file.strip(".flag") for file in os.listdir("dump/") if file.endswith(".flag")]:
            if flag.split("_at_")[1] < datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'):
                os.remove(f"dump/{flag}.flag")

    # pylint: disable=broad-except
    @classmethod
    def notify(cls, function: Callable[[Any], Any]) -> Callable[[Any], Any]:
        """
        Данный метод класса выполняет функцию декоратора и позволяет регистрировать ошибки в
        других методах и сообщать о них администратору бота.

        :param function: функция, которую надо задекорировать.
        :return: вызываемый объект (Callable).
        """
        @wraps(function)
        def error_handler(*args, **kwargs) -> Any | None:
            try:
                result = function(*args, **kwargs)
                return result
            except BaseException as exc:
                if cls._bot_config["debug_mode"]:
                    playsound.playsound("assets/sounds/critical_stop.wav")

                cls.create_exception_flag(exc.__class__.__name__, traceback.format_exc())
                cls._vk_session.method("messages.send", {
                    "peer_id": cls._bot_config["lead_admin_vk_id"],
                    "user_id": cls._bot_config["lead_admin_vk_id"],
                    "message": f"Было вызвано исключение '{exc.__class__.__name__}' в методе {function.__name__}.\n" +
                               f"{traceback.format_exc()}",
                    "random_id": random.randint(Consts.RANDINT_BOTTOM_BOUND, Consts.RANDINT_TOP_BOUND),
                    "payload": json.dumps({
                        "is_bot": True
                    })
                })

            return None

        return error_handler
