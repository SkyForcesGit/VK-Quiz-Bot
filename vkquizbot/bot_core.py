# Package name: vkquizbot
# Module name: bot_core.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс BotCore, который является ядром композиции программы и
осуществляет связь между своими компонентами.

Список классов и методов:
| BotCore
    Данный класс является ядром композиции программы, выполняя роль связующего звена для всех
    компонентов, которые инстанцируются им.

⌊__ __data_check [PRIVATE]
        Данный метод проверяет файл конфига бота на элементарное соответствие типам и
        значениям полей.

Подробную информацию о методах и классах ищите в документации к непосредственно им.

Информацию о доступных атрибутах класса смотрите в документации класса.
"""

# Стандартная библиотека
import threading
import os
import json
import shutil
import datetime
from zipfile import ZipFile

# Модули бота
from .console import Console
from .handler import Handler
from .listener import Listener
from .logger import Logger
from .messenger import Messenger
from .user_manager import UserManager
from .quiz_manager import QuizManager
from .data_manager import DataManager


# pylint: disable=too-many-instance-attributes
class BotCore:
    """
    Данный класс является ядром композиции программы, выполняя роль связующего звена для всех
    компонентов, которые инстанцируются им. Более того, класс совершает все необходимые
    операции для инициализации бота и его работы.

    Конструктор класса:
    Данный метод инстанцирует основные компоненты бота, осуществляет копирование временных
    файлов в рабочие директории, инициирует проверку файла конфигурации, задает основные атрибуты.

    Список публичных методов:
    Отсутствует.

    Список доступных атрибутов класса:
    | logger
    | data_manager
    | console
    | handler
    | listener
    | messenger
    | user_manager
    | quiz_manager
    | quiz_manager
    | answer_block
    | stop_event
    | quiz_thread
    """
    def __init__(self) -> None:
        self.__data_check()
        shutil.copyfile("dump/temp_info.json", "data/temp_info.json")

        dir_name = "logs/"

        if dir_name.strip("/") in os.listdir():
            logs_listdir = [file for file in os.listdir(dir_name) if file.endswith(".log")]

            if logs_listdir:
                with ZipFile(f"{dir_name}logs_before_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip",
                             mode="w") as archive:
                    for file in logs_listdir:
                        archive.write(f"{dir_name}{file}")

            for file in logs_listdir:
                os.remove(f"{dir_name}{file}")
        else:
            os.mkdir(dir_name)

        self._logger = Logger()
        self._data_manager = DataManager(self)
        self._console = Console(self)
        self._handler = Handler(self)
        self._listener = Listener(self)
        self._messenger = Messenger(self)
        self._user_manager = UserManager(self)
        self._quiz_manager = QuizManager(self)

        self._answer_block = True

        self._stop_event = threading.Event()
        self._quiz_thread = threading.Thread(target=None)

    # pylint: disable=too-many-branches
    @staticmethod
    def __data_check() -> None:
        """
        Данный статический метод проверяет файл конфига бота на элементарное соответствие типам и
        значениям полей. В случае несоответствия генерируется исключение.

        :except ValueError: вызывается, если какое-либо значение поля не прошло проверку.
        :except TypeError: вызывается, если какое-либо поле не прошло проверку типов.
        :return: ничего (None).
        """
        with open("data/bot_config.json", mode="r", encoding="utf-8") as __bot_config:
            __bot_config = json.load(__bot_config)

        if not isinstance(__bot_config["VK_API_community_Access_Key"], str):
            raise TypeError("Ключ VK API должен быть строкой.")

        if isinstance(__bot_config["Group_ID"], int):
            if __bot_config["Group_ID"] < 0:
                raise ValueError("ID группы должен быть положительным числом.")
        else:
            raise TypeError("ID группы должен иметь тип 'int'.")

        if isinstance(__bot_config["Lead_Admin_VK_ID"], int):
            if __bot_config["Lead_Admin_VK_ID"] < 0:
                raise ValueError("ID администратора бота должен быть положительным числом.")
        else:
            raise TypeError("ID администратора бота должен иметь тип 'int'.")

        if isinstance(__bot_config["Chat_for_work_ID"], int):
            if __bot_config["Chat_for_work_ID"] < 0:
                raise ValueError("ID рабочего чата должен быть положительным числом.")
        else:
            raise TypeError("ID рабочего чата должен иметь тип 'int'.")

        if not __bot_config["Quiz_mode"] in ["Normal", "Blitz", "Score"]:
            raise ValueError("Бот работает только в двух режимах викторины: 'Normal', 'Score' и 'Blitz'.")

        if isinstance(__bot_config["Time_on_quiz_round"], int | float):
            if __bot_config["Time_on_quiz_round"] < 0:
                raise ValueError("Количество времени на раунд викторины должно быть положительным числом.")
        else:
            raise TypeError("Количество времени на раунд викторины должно иметь тип 'int' или 'float'.")

        if not isinstance(__bot_config["Random_selection_for_quiz_questions"], bool):
            raise TypeError("Значение параметра рандомного выбора вопросов должно иметь тип 'bool'.")

        if not isinstance(__bot_config["Ignore_save_state"], bool):
            raise TypeError("Значение параметра игнорирования точек восстановления должно иметь тип 'bool'.")

        if not isinstance(__bot_config["Force_load_save_state"], bool):
            raise TypeError("Значение параметра форсированной загрузки точки восстановления должно иметь тип 'bool'.")

        if not isinstance(__bot_config["Debug_mode"], bool):
            raise TypeError("Значение параметра использования дебаг-режима должно иметь тип 'bool'.")

    def __del__(self) -> None:
        """
        Данная функция отвечает за удаление всех объектов бота и завершение его работы.

        :return: ничего (None).
        """
        self._stop_event.set()
        if self._quiz_thread.is_alive():
            self._quiz_thread.join()

        os.remove("data/temp_info.json")

    # A lot of properties, nothing interesting.
    # pylint: disable=missing-function-docstring
    @property
    def answer_block(self) -> bool:
        return self._answer_block

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def console(self) -> Console:
        return self._console

    @property
    def handler(self) -> Handler:
        return self._handler

    @property
    def listener(self) -> Listener:
        return self._listener

    @property
    def messenger(self) -> Messenger:
        return self._messenger

    @property
    def user_manager(self) -> UserManager:
        return self._user_manager

    @property
    def quiz_manager(self) -> QuizManager:
        return self._quiz_manager

    @property
    def data_manager(self) -> DataManager:
        return self._data_manager

    @property
    def stop_event(self) -> threading.Event:
        return self._stop_event

    @property
    def quiz_thread(self) -> threading.Thread:
        return self._quiz_thread

    @answer_block.setter
    def answer_block(self, new_value: bool) -> None:
        self._answer_block = new_value

    @quiz_thread.setter
    def quiz_thread(self, new_thread: threading.Thread) -> None:
        self._quiz_thread = new_thread
