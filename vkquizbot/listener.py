# Package name: vkquizbot
# Module name: listener.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Listener, который реализует методы бота по обработке
различных событий: отправка сообщений, нажатие на кнопку клавиатуры бота и т.д.

Список классов и методов:
| Listener(UtilsInitLongpoll)
    Данный класс отвечает за работу различных слушателей, которые ловят информацию о
    поступивших событиях и сообщениях.

⌊__ main_listener
        Данный метод отслеживает все новые сообщения от пользователей и передает в
        основной обработчик.

⌊__ bot_answers_listener
        Данный метод отслеживает все новые сообщения от бота, сохраняет "сырую" информацию
        о них и передает в обработчик ответов бота.

⌊__ members_quiz_answers_listener
        Данный метод отслеживает все нажатия на callback-кнопки клавиатуры бота, и
        отправляет информацию о них в обработчик ответов пользователей.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import threading

# Сторонние библиотеки
from vk_api.longpoll import VkEventType
from vk_api.bot_longpoll import VkBotEventType

# Модули бота
from .utils import UtilsInitLongpoll, ErrorNotifier


class Listener(UtilsInitLongpoll):
    """
    Данный класс отвечает за работу различных слушателей, которые ловят информацию о
    поступивших событиях и сообщениях для последующей отправки их в методы-обработчики
    класса Handler.

    Конструктор класса:
    Метод отвечает за первичную инициализацию слушателя данных.
    Создает логгер для объекта слушателя, а также создает "среду" для работы с VK API.

    :param parent: ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | main_listener
    | bot_answers_listener
    | members_quiz_answers_listener
    """

    @ErrorNotifier.notify
    def __init__(self, parent) -> None:
        self.__parent = parent
        self.__listener_logger, self.__main_listener_logger, self.__bot_answers_listener_logger,\
            self.__members_quiz_answers_listener_logger = self.__parent.logger.get_multiple_loggers("listeners")
        super().__init__()

        self.__listener_logger.debug("Токен VK для работы бота получен.")
        self.__listener_logger.debug("'Longpoll' и 'Bot_longpoll' инициализированы.")
        self.__listener_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__listener_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                     f"\n{'=' * 30}[Конец логгирования]{'=' * 30}")

    @ErrorNotifier.notify
    def main_listener(self) -> None:
        """
        Данный метод отслеживает все новые сообщения от пользователей, сохраняет их текст и
        передает в основной обработчик 'main_handler' для последующей обработки данных.

        :return: ничего (None).
        """
        self.__main_listener_logger.debug("Метод 'main_listener' запущен.")

        for event in self._longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_message = event.text.lower()
                message_info = event.raw

                threading.Thread(target=self.__parent.handler.main_handler, args=[user_message, message_info,
                                                                                  event.user_id],
                                 name="MainHandlerThread").start()
                self.__main_listener_logger.debug("Метод 'main_listener' вызвал метод 'main_listener_handler'.\n" +
                                                  '\t' * 9 + f" Текст сообщения - '{user_message}'\n")

    @ErrorNotifier.notify
    def bot_answers_listener(self) -> None:
        """
        Данный метод отслеживает все новые сообщения от бота, сохраняет полную "сырую" информацию
        о них и передает в обработчик ответов бота 'bot_question_messages_handler' для последующей
        обработки данных.

        :return: ничего (None).
        """
        self.__bot_answers_listener_logger.debug("Метод 'bot_answers_listener' запущен.")

        for event in self._longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and not event.to_me:
                message_info = event.raw

                threading.Thread(target=self.__parent.handler.bot_question_messages_handler, args=[message_info],
                                 name="BotQuestionMessagesHandlerThread").start()
                self.__bot_answers_listener_logger.debug("Метод 'bot_answers_listener' вызвал метод " +
                                                         "'bot_question_messages_handler'.\n" +
                                                         '\t' * 10 + f"  Информация о сообщении - '{message_info}'\n")

    @ErrorNotifier.notify
    def members_quiz_answers_listener(self) -> None:
        """
        Данный метод отслеживает все события нажатия пользователей на callback-кнопки клавиатуры
        бота, записывает "сырую" информацию о них и отправляет в обработчик ответов пользователей
        на вопросы викторины 'members_quiz_answers_handler'.

        :return: ничего (None).
        """
        self.__members_quiz_answers_listener_logger.debug("Метод 'members_answers_listener' запущен.")

        for event in self._bot_longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_EVENT:
                callback_answer = event.raw

                self.__members_quiz_answers_listener_logger.debug(f"Сырой Callback-ответ: {callback_answer}")
                threading.Thread(target=self.__parent.handler.members_quiz_answers_handler,
                                 args=[callback_answer], name="MembersQuizAnswersThread").start()
                self.__members_quiz_answers_listener_logger.debug("Метод 'members_answers_listener' вызвал метод " +
                                                                  "'members_answers_handler'.\n")
