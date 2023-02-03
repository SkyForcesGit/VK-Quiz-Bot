# Package name: vkquizbot
# Module name: data_manager.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс DataManager, который реализует методы для работы с различными
файловыми структурами данных.

Список классов и методов:
| DataManager(UtilsInitDefault)
    Данный класс осуществляет работу (чтение, запись) с различными структурами данных.

⌊__ load_json
        Данный метод загружает JSON-файл.

⌊__ load_jsons
        Данный метод загружает сразу несколько JSON-файлов.

⌊__ pickle_dump
        Данный метод сериализует в bin-файл с указанным именем различные данные.

⌊__ pickle_load
        Данный метод десериализует bin-файл с указанным именем.

⌊__ __pickle_load_generator [PRIVATE]
        Данный генератор последовательно возвращает по одному значению из загруженного
        bin-файла.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import json
import pickle
import os
import traceback
import time
from typing import Any

# Сторонние библиотеки
import playsound
import loguru

# Модули бота
from .utils import ErrorNotifier, UtilsInitDefault
from .consts import Consts


class DataManager(UtilsInitDefault):
    """
    Данный класс осуществляет работу (чтение, запись) с различными данными в таких типах файлов
    как JSON и BIN.

    Конструктор класса:
    Данный метод осуществляет загрузку файла конфигурации бота, который необходим для
    дальнейшей работы экземпляра класса.

    :param parent: ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | load_json
    | load_jsons
    | pickle_dump
    | pickle_load
    """

    def __init__(self, parent):
        self.__parent = parent
        super().__init__()

    @ErrorNotifier.notify
    def load_json(self, file_name: str, load_logger: loguru.logger = None) -> dict:
        """
        Данный метод загружает JSON-файл и возвращает его в виде словаря методу, который
        его запросил.

        :param file_name: имя JSON-файла, который нужно загрузить (Без расширения).
        :param load_logger: ожидается экземпляр класса loguru.logger.
        :except FileNotFoundError: вызывается, если файл не был найден в директории 'data'.
        :return: словарь с данными.
        """
        if f"{file_name}.json" not in os.listdir("data/"):
            raise FileNotFoundError(f"Файл '{file_name}' отсутствует в директории 'data'.")

        while True:
            try:
                with open(f"data/{file_name}.json", mode="r", encoding="utf-8") as json_info:
                    result = json.load(json_info)

                    if load_logger is not None:
                        load_logger.debug(f"JSON-файл '{file_name}' был успешно загружен.")

                    return result
            except json.decoder.JSONDecodeError as exc:
                str_ = f"Возбуждено исключение '{exc.__class__.__name__}', в JSON-файле '{file_name}', вероятно, " +\
                       "синтаксическая ошибка. Отредактируйте файл, и программа повторит попытку загрузки."

                if load_logger is not None:
                    load_logger.debug(str_)

                self.__parent.messenger.send_message(str_, {"to_admin": True})
                self.__parent.messenger.send_message(traceback.format_exc(), {"to_admin": True})

                if self._bot_config["debug_mode"]:
                    playsound.playsound("assets/sounds/critical_stop.wav")

                file_modification_time = os.path.getmtime(f"data/{file_name}.json")

                while True:
                    if file_modification_time != os.path.getmtime(f"data/{file_name}.json"):
                        break
                    time.sleep(Consts.TIME_DELAY_5)
                continue

    @ErrorNotifier.notify
    def load_jsons(self, file_names_list: list, load_logger: loguru.logger = None) -> list:
        """
        Данный метод загружает сразу несколько JSON-файлов и возвращает их в виде списка тому методу,
        который запросил данные.

        :param file_names_list: имена JSON-файлов, которые нужно загрузить (Без расширения).
        :param load_logger: ожидается экземпляр класса loguru.logger.
        :return: список с загруженными данными.
        """
        result_list = []

        for file in file_names_list:
            result_list.append(self.load_json(file, load_logger))

        return result_list

    @staticmethod
    @ErrorNotifier.notify
    def pickle_dump(file_name: str, data_to_dump: list) -> None:
        """
        Данный статический метод сериализует в bin-файл с указанным именем данные, указанные в
        списке.

        :param file_name: имя будущего bin-файла.
        :param data_to_dump: список с данными, которые необходимо сериализовать (без расширения).
        :return: ничего (None).
        """
        with open(f"dump/{file_name}.bin", "wb") as dump_file:
            for data in data_to_dump:
                pickle.dump(data, dump_file)

    @staticmethod
    @ErrorNotifier.notify
    def __pickle_load_generator(pickle_file) -> Any:
        """
        Данный статический генератор последовательно возвращает по одному значению из загруженного
        bin-файла с сериализованными данными.

        :param pickle_file: bin-файл, из которого ведется загрузка.
        :return: любое значение (Any).
        """
        try:
            while True:
                yield pickle.load(pickle_file)
        except EOFError:
            pass

    @classmethod
    @ErrorNotifier.notify
    def pickle_load(cls, file_name: str) -> list[Any]:
        """
        Данный метод класса десериализует bin-файл с указанным именем и помещает все полученные
        значения в список.

        :param file_name: имя bin-файла, который нужно десериализовать (без расширения).
        :return: список с полученными значениями.
        """
        data_list = []

        with open(f"dump/{file_name}.bin", "rb") as dump_file:
            for data in cls.__pickle_load_generator(dump_file):
                data_list.append(data)

        return data_list
