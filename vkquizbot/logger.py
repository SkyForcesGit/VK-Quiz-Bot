# Package name: vkquizbot
# Module name: logger.py
# Author(s): SkyForces
# Modification date: February 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Logger, который отвечает за создание и настройку различных
логгеров.

Список классов и методов:
| Logger
    Данный класс отвечает за создание и настройку логгеров, необходимых для работы всей
    программы бота.

⌊__ get_single_logger
        Данный метод создает новый логгер с заданными настройками.

⌊__ get_multiple_loggers
        Данный метод создает группу логгеров с заданными настройками.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import json

# noinspection PyProtectedMember
# Сторонние библиотеки
import loguru
from loguru import _logger as _builder

# Модули бота
from .utils import ErrorNotifier
from .consts import Consts


class Logger:
    """
    Данный класс отвечает за создание и настройку логгеров, необходимых для работы всей
    программы бота.

    Конструктор класса:
    Данный метод задает логгер, который регистрирует все последующие действия конструктора
    по созданию логгеров.

    Список публичных методов:
    | get_single_logger
    | get_multiple_loggers
    """
    @ErrorNotifier.notify
    def __init__(self) -> None:
        self.__log_builder_logger = _builder.Logger(core=_builder.Core(), exception=None, depth=0, record=False,
                                                    lazy=False, colors=False, raw=False, capture=True, extra={},
                                                    patcher=None)

        with open("data/logger_configs/log_builder.json", encoding="utf-8") as logger_config:
            logger_config = json.load(logger_config)

            self.__log_builder_logger.configure(**logger_config["config"])
            self.__log_builder_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__log_builder_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                        Consts.END_OF_LOGS_LINE)

    @ErrorNotifier.notify
    def get_single_logger(self, logger_config_name: str) -> loguru.logger:
        """
        Данный метод создает новый логгер с определенными настройками, прописанными в JSON-файле
        конфигурации из data/logger_configs, и возвращает его запросившему логгер объекту.

        :param logger_config_name: название файла конфигурации логгера из data/logger_configs
        (Без расширения).
        :return: экземпляр класса 'loguru.logger'.
        """
        self.__log_builder_logger.debug(f"Построение логгера '{logger_config_name}' начато.")

        building_logger = _builder.Logger(core=_builder.Core(), exception=None, depth=0, record=False, lazy=False,
                                          colors=False, raw=False, capture=True, extra={}, patcher=None)

        with open(f"data/logger_configs/{logger_config_name}.json", encoding='utf-8') as logger_config:
            logger_config = json.load(logger_config)

            building_logger.configure(**logger_config["config"])
            self.__log_builder_logger.debug(f"Логгер '{logger_config_name}' успешно создан.\n" +
                                            f"{Consts.TAB_SPACE_6}Конфигурация: {logger_config['config']}\n")

        return building_logger

    @ErrorNotifier.notify
    def get_multiple_loggers(self, loggers_config_name: str) -> list[loguru.logger]:
        """
        Данный метод создает группу логгеров с настройками, прописанными в JSON-файле конфигурации
        из data/logger_configs, и возвращает ее запросившему логгеры объекту.

        :param loggers_config_name: название файла конфигурации логгеров из data/logger_configs
        (Без расширения).
        :return: список экземпляров класса 'loguru.logger'.
        """
        self.__log_builder_logger.debug(f"Построение логгеров из '{loggers_config_name}' начато.")

        built_loggers = []

        with open(f"Data/Logger_configs/{loggers_config_name}.json", encoding='utf-8') as loggers_config:
            loggers_config = json.load(loggers_config)
            for config in loggers_config["configs"]:
                building_logger = _builder.Logger(core=_builder.Core(), exception=None, depth=0, record=False,
                                                  lazy=False, colors=False, raw=False, capture=True, extra={},
                                                  patcher=None)

                building_logger.configure(**loggers_config["configs"][config])
                self.__log_builder_logger.debug(f"Логгер '{config}' успешно создан.\n" +
                                                f"{Consts.TAB_SPACE_6}Конфигурация: " +
                                                f"{loggers_config['configs'][config]}\n")
                built_loggers.append(building_logger)

        return built_loggers
