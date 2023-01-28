# Package name: vkquizbot
# Module name: handler.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Handler, который реализует методы работы бота по обработке
входящей информации, а также модификации и идентификации различных свойств исходящих данных.

Список классов и методов:
| Handler(UtilsInitVKAPI)
    Данный класс отвечает за работу различных обработчиков данных, поступающих боту.
    Методы класса обрабатывают полученные/отправленные события и сообщения.

⌊__ main_handler
        Данный метод обрабатывает текстовые сообщения от пользователей, пойманные основным
        слушателем.

⌊__ bot_question_messages_handler
        Данный метод отвечает за обработку всех новых сообщений, пойманных слушателем ответов бота.

⌊__ members_quiz_answers_handler
        Данный метод обрабатывает события, созданные в результате нажатия callback-кнопок на
        клавиатуре бота.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import json
import threading

# Модули бота
from .utils import UtilsInitVKAPI, ErrorNotifier


class Handler(UtilsInitVKAPI):
    """
    Данный класс отвечает за работу различных обработчиков данных, поступающих боту.
    Методы этого класса обрабатывают события и сообщения, отправляемые участниками беседы,
    а также ответы бота на них.

    Конструктор класса:
    Метод отвечает за первичную инициализацию обработчика данных.
    Создает логгер для объекта обработчика, а также создает "среду" для работы с VK API.

    :param parent: ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | main_handler
    | bot_question_messages_handler
    | members_quiz_answers_handler
    """
    @ErrorNotifier.notify
    def __init__(self, parent) -> None:
        self.__parent = parent
        self.__handler_logger, self.__main_handler_logger, self.__bot_question_messages_handler,\
            self.__members_quiz_answers_handler = self.__parent.logger.get_multiple_loggers("handlers")
        super().__init__()

        self.__handler_logger.debug("Токен VK для работы бота получен.")
        self.__handler_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__handler_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                    f"\n{'=' * 30}[Конец логгирования]{'=' * 30}")

    @ErrorNotifier.notify
    def main_handler(self, user_message: str, user_id: int) -> None:
        """
        Данный метод обрабатывает текстовые сообщения от пользователей, пойманные основным
        слушателем 'main_listener'. Основная его задача - выследить команды, начинающиеся
        с '/' ('/start', '/get_chat' и т.д.).

        :param user_message: текст сообщения пользователя, полученного от 'main_listener'.
        :param user_id: ID страницы VK пользователя, который отправил сообщение, полученный от
        'main_listener'.
        :return: ничего (None).
        """
        self.__main_handler_logger.debug("Метод 'main_handler' запущен.")

        with self._locker:
            temp_info = self.__parent.data_manager.load_json("temp_info", self.__main_handler_logger)

            match user_message:
                case "/get_chat":
                    if user_id not in temp_info["Admin_VK_pages_IDs"]:
                        if not temp_info["Get_chat_first_start"]:
                            self.__main_handler_logger.debug("Метод 'main_handler' вернул значение 'None'.\n" +
                                                             '\t' * 9 + "Команда пользователя - '/get_chat'.\n")
                            self.__parent.messenger.send_message("Для использования данной команды вы должны иметь " +
                                                                 "права администратора.")
                            return None

                    temp_info["Get_chat_first_start"] = False

                    self.__parent.data_manager.rewrite_json(temp_info, "temp_info", self.__main_handler_logger)

                    threading.Thread(target=self.__parent.user_manager.get_chat, name="UserManagerThread").start()
                    self.__main_handler_logger.debug("Метод 'get_chat' был запущен.")

                case "/start":
                    if user_id in temp_info["Admin_VK_pages_IDs"]:
                        if not temp_info["Start_function_first_start"]:
                            self.__main_handler_logger.debug("Метод 'main_handler' вернул значение 'None'.\n" +
                                                             '\t' * 9 + "Команда пользователя - '/start'\n")
                            self.__parent.messenger.send_message("Викторина уже запущена.")
                            return None

                        temp_info["Start_function_first_start"] = False

                        self.__parent.data_manager.rewrite_json(temp_info, "temp_info", self.__main_handler_logger)

                        self.__parent.quiz_thread = threading.Thread(target=self.__parent.quiz_manager.quiz_mainloop,
                                                                     daemon=True, name="QuizMainloopThread")

                        self.__parent.quiz_thread.start()
                        self.__main_handler_logger.debug("Метод 'quiz_mainloop' был запущен.")
                    else:
                        self.__parent.messenger.send_message("Для использования данной команды вы должны иметь " +
                                                             "права администратора.")

                case "/kick_all":
                    if user_id in temp_info["Admin_VK_pages_IDs"]:
                        self.__parent.messenger.send_message("Начат процесс исключения участников...")
                        self.__parent.user_manager.kick_all_users()
                        self.__parent.messenger.send_message("Все участники были успешно исключены.")
                        self.__main_handler_logger.debug("Все участники были успешно исключены.")
                    else:
                        self.__parent.messenger.send_message("Для использования данной команды вы должны иметь " +
                                                             "права администратора.")

        self.__main_handler_logger.debug("Метод 'main_handler' успешно завершил работу.\n")
        return None

    @ErrorNotifier.notify
    def bot_question_messages_handler(self, bot_answer_data: list) -> None:
        """
        Данный метод отвечает за обработку всех новых сообщений, пойманных слушателем ответов бота
        'bot_answers_listener', с целью найти среди них сообщения, отправленные ботом и содержащие
        в себе клавиатуру. Нахождение подобного будет сигналом о том, что бот отправил новый вопрос
        викторины. ID такого сообщения будет записан и использован в будущем.

        :param bot_answer_data: "сырая" информация о сообщении, полученная из 'bot_answers_listener'.
        :return: ничего (None).
        """
        self.__bot_question_messages_handler.debug("Метод 'bot_question_messages_handler' запущен.")

        if dict(bot_answer_data[6]).get("payload") is not None and dict(bot_answer_data[6]).get("keyboard") is not None:
            if dict(bot_answer_data[6]["keyboard"]).get("buttons") is not None:
                _current_id_of_message_question = bot_answer_data[1]

                with self._locker:
                    temp_info = self.__parent.data_manager.load_json("temp_info",
                                                                     self.__bot_question_messages_handler)
                    temp_info["Current_ID_of_latest_quiz_message"] = _current_id_of_message_question

                    self.__parent.data_manager.rewrite_json(temp_info, "temp_info",
                                                            self.__bot_question_messages_handler)

                self.__bot_question_messages_handler.debug("Метод 'bot_question_messages_handler' успешно " +
                                                           "завершил работу.\n" +
                                                           '\t' * 11 + "     ID последнего вопроса " +
                                                           f"- {_current_id_of_message_question}\n")
        else:
            self.__bot_question_messages_handler.debug("Метод 'bot_question_messages_handler' не распознал " +
                                                       "в сообщении вопрос.\n")

    # pylint: disable=too-many-nested-blocks
    @ErrorNotifier.notify
    def members_quiz_answers_handler(self, event_data: dict) -> None:
        """
        Данный метод обрабатывает события, созданные в результате нажатия callback-кнопок на
        клавиатуре бота и пойманные слушателем ответов участников на вопросы викторины
        'members_quiz_answers_listener', а также посылает необходимый ответ на них, попутно ведя
        учет ответивших участников.

        :param event_data: "сырая" информация о событии, полученная от
        'members_quiz_answers_listener'.
        :return: ничего (None).
        """
        self.__members_quiz_answers_handler.debug("Метод 'members_answers_handler' запущен.")

        with self._locker:
            json_texts, temp_info = self.__parent.data_manager.load_jsons(["texts_for_messages", "temp_info"],
                                                                          self.__members_quiz_answers_handler)
            current_user_id = event_data["object"]["user_id"]
            current_payload = event_data["object"]["payload"]["answer"]
            current_event_id = event_data["object"]["event_id"]

            self.__members_quiz_answers_handler.debug(f"Текущий ID пользователя: {current_user_id}\n" +
                                                      '\t' * 11 + f"Текущий ID события: {current_event_id}\n" +
                                                      '\t' * 11 + f"Текущий пэйлод: {current_payload}")

            if not self.__parent.answer_block:
                if current_user_id not in temp_info["Admin_VK_pages_IDs"]:
                    if current_user_id not in temp_info["Members_answered_on_quiz"]:
                        if current_payload:
                            if self._bot_config["Quiz_mode"] == "Score":
                                if str(current_user_id) not in list(temp_info["Members_scores"].keys()):
                                    temp_info["Members_scores"].update({current_user_id: 1})
                                else:
                                    temp_info["Members_scores"][str(current_user_id)] += 1
                                self.__members_quiz_answers_handler.debug(f"Пользователю {current_user_id} успешно " +
                                                                          "начислен балл.")
                            else:
                                temp_info["Members_answered_on_quiz_right"].append(current_user_id)
                                self.__members_quiz_answers_handler.debug(f"Пользователь {current_user_id} добавлен " +
                                                                          "в список успешно ответивших.")

                        temp_info["Members_answered_on_quiz"].append(current_user_id)

                        self.__parent.data_manager.rewrite_json(temp_info, "temp_info",
                                                                self.__members_quiz_answers_handler)

                        event_answer_text = json_texts["answer_got_text"]
                    else:
                        event_answer_text = json_texts["already_answered_text"]
                else:
                    event_answer_text = json_texts["admin_cannot_answer_text"]
            else:
                event_answer_text = json_texts["answer_blocked_text"]

            self._vk_session.method("messages.sendMessageEventAnswer", {
                "event_id": current_event_id,
                "user_id": current_user_id,
                "peer_id": 2000000000 + self._bot_config["Chat_for_work_ID"],
                "event_data": json.dumps({
                    "type": "show_snackbar",
                    "text": event_answer_text
                })
            })
            self.__members_quiz_answers_handler.debug(f"Пользователь {current_user_id} получил ответ " +
                                                      "на Callback-событие.\n")
