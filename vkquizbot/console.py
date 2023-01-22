# Package name: vkquizbot
# Module name: console.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Console, который реализует примитивные методы для управления
некоторыми аспектами работы бота.

Список классов и методов:
| Console
    Данный класс отвечает за работу примитивной консоли для управления ботом.

⌊__ __start_bot [PRIVATE]
        Данный метод отвечает за запуск бота, а если быть точнее, то за запуск двух основных
        слушателей.

⌊__ __console_terminate [PRIVATE]
        Данный метод отвечает за завершение работы консоли, которое провоцирует завершение работы
        бота.

⌊__ __archives_remove [PRIVATE]
        Данный метод отвечает за удаление всех архивов с логами бота.

⌊__ console_mainloop
        Данный метод отвечает за обработку команд администратора к консоли бота.
"""

# Стандартная библиотека
import time
import threading
import os

# Модули бота
from .utils import ErrorNotifier


class Console:
    """
    Данный класс отвечает за работу примитивной консоли для управления ботом.

    Конструктор класса:
    Метод отвечает за первичную инициализацию объекта консоли.
    Также создает логгер для объекта консоли.

    :param parent: ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | console_mainloop
    """
    @ErrorNotifier.notify
    def __init__(self, parent) -> None:
        self.__parent = parent
        self.__console_logger = self.__parent.logger.get_single_logger("console")

        self.__console_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__console_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                    f"\n{'=' * 30}[Конец логгирования]{'=' * 30}")

    def __start_bot(self) -> None:
        """
        Данный метод отвечает за запуск бота, а если быть точнее, то за запуск двух основных
        слушателей.

        :return: ничего (None).
        """
        self.__console_logger.debug("Метод 'start_bot' запущен.")

        threading.Thread(target=self.__parent.listener.main_listener, daemon=True,
                         name="MainListenerThread").start()
        threading.Thread(target=self.__parent.listener.bot_answers_listener, daemon=True,
                         name="BotAnswersListenerThread").start()

        self.__console_logger.debug("Методы 'main_listener' и 'bot_answers_listener' запущены.\n")
        print("\nБот успешно запущен.")

    def __console_terminate(self) -> None:
        """
        Данный метод отвечает за завершение работы консоли, которое провоцирует завершение работы
        бота.

        :return: ничего (None).
        """
        self.__console_logger.debug("Метод 'console_terminate' запущен.")

        print("\nВы осуществите выход из программы, как только все фоновые потоки корректно завершат работу.", end=' ')
        for _ in range(4):
            print(".", end=" ")
            time.sleep(1)

    def __archives_remove(self) -> None:
        """
        Данный метод отвечает за удаление всех архивов с логами бота.

        :return: ничего (None).
        """
        self.__console_logger.debug("Метод 'archives_remove' запущен.")

        for file in [file_ for file_ in os.listdir("logs/") if file_.endswith(".zip")]:
            os.remove(f"logs/{file}")

        self.__console_logger.debug("Все архивы с логами были удалены.")
        print("\nВсе архивы с логами удалены.")

    def console_mainloop(self) -> None:
        """
        Данный метод отвечает за обработку команд администратора к консоли бота.

        :return: ничего (None).
        """
        self.__console_logger.debug("Метод 'console_mainloop' запущен.")
        self.__start_bot()

        while True:
            command = input("CONSOLE >> ")

            match command:
                case "/exit":
                    self.__console_terminate()
                    return None
                case "/threads":
                    print("\n" + str(threading.enumerate()))
                case "/rem_arcs":
                    self.__archives_remove()
                case _:
                    print("\nНеверная команда, повторите попытку ввода.")
