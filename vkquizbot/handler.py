# Package name: vkquizbot
# Module name: handler.py
# Author(s): SkyForces
# Modification date: February 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Handler, который реализует методы работы бота по обработке
входящей информации, а также модификации и идентификации различных свойств исходящих данных.

Список классов и методов:
| HandlerException(BaseException)
    Данный тип исключений используется во время обработки информации обработчиками.

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

⌊__ __get_chat_handler [PRIVATE]
        Данный метод вызывается 'main_handler' при получении команды '/get_chat'.

⌊__ __start_handler [PRIVATE]
        Данный метод вызывается 'main_handler' при получении команды '/start'.

⌊__ __kick_all_handler [PRIVATE]
        Данный метод вызывается 'main_handler' при получении команды '/kick_all'.

⌊__ __kick_handler [PRIVATE]
        Данный метод вызывается 'main_handler' при получении команды '/kick'.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import json
import threading

# Модули бота
from .utils import UtilsInitVKAPI, ErrorNotifier
from .consts import Consts


class HandlerException(BaseException):
    """
    Данный тип исключений используется во время обработки информации обработчиками и в основном
    вызывается в те моменты, когда нужно спровоцировать отправку определенного сообщения вследствие
    не пройденных проверок информации.
    """


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
        self.__handler_logger, self.__main_handler_logger, self.__bot_question_messages_handler, \
            self.__members_quiz_answers_handler = self.__parent.logger.get_multiple_loggers("handlers")
        self.__texts_for_messages = self.__parent.data_manager.load_json("texts_for_messages",
                                                                         self.__members_quiz_answers_handler)
        super().__init__()

        self.__handler_logger.debug("Токен VK для работы бота получен.")
        self.__handler_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__handler_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                    Consts.END_OF_LOGS_LINE)

    def __get_chat_handler(self, raw_info: list, user_id: int) -> None:
        """
        Данный приватный метод вызывается 'main_handler' при получении команды '/get_chat' и
        выполняет действия по запуску соответствующего команде метода.

        :param raw_info: "сырая" информация о сообщении, полученная от 'main_handler'.
        :param user_id: ID пользователя, отправившего сообщение, полученный от 'main_handler'.
        :return: ничего (None).
        """
        try:
            if user_id not in self.__parent.temp_info.admin_vk_pages_ids:
                if not self.__parent.temp_info.get_chat_first_start:
                    raise HandlerException("do_not_have_admin_rights_text")

            self.__parent.temp_info.get_chat_first_start = False

            threading.Thread(target=self.__parent.user_manager.get_chat, args=[raw_info],
                             name="UserManagerThread").start()
            self.__main_handler_logger.debug("Метод 'get_chat' был запущен.")
        except HandlerException as exc:
            self.__parent.messenger.send_message(str(exc), {"reply": raw_info[1]})
            self.__main_handler_logger.debug("Метод 'main_handler' вернул значение 'None'.\n" +
                                             f"{Consts.TAB_SPACE_9}Команда пользователя - '/get_chat'.\n")

    def __start_handler(self, raw_info: list, user_id: int) -> None:
        """
        Данный приватный метод вызывается 'main_handler' при получении команды '/start' и
        выполняет действия по запуску соответствующего команде метода.

        :param raw_info: "сырая" информация о сообщении, полученная от 'main_handler'.
        :param user_id: ID пользователя, отправившего сообщение, полученный от 'main_handler'.
        :return: ничего (None).
        """
        try:
            if user_id not in self.__parent.temp_info.admin_vk_pages_ids:
                raise HandlerException("do_not_have_admin_rights_text")
            if not self.__parent.temp_info.start_function_first_start:
                raise HandlerException("quiz_already_started_text")

            self.__parent.temp_info.start_function_first_start = False
            self.__parent.quiz_thread = threading.Thread(target=self.__parent.quiz_manager.quiz_mainloop,
                                                         daemon=True, name="QuizMainloopThread")

            self.__parent.quiz_thread.start()
            self.__main_handler_logger.debug("Метод 'quiz_mainloop' был запущен.")
        except HandlerException as exc:
            self.__parent.messenger.send_message(str(exc), {"reply": raw_info[1]})
            self.__main_handler_logger.debug("Метод 'main_handler' вернул значение 'None'.\n" +
                                             f"{Consts.TAB_SPACE_9}Команда пользователя - '/start'\n")

    def __kick_all_handler(self, raw_info: list, user_id: int) -> None:
        """
        Данный приватный метод вызывается 'main_handler' при получении команды '/kick_all' и
        выполняет действия по запуску соответствующего команде метода.

        :param raw_info: "сырая" информация о сообщении, полученная от 'main_handler'.
        :param user_id: ID пользователя, отправившего сообщение, полученный от 'main_handler'.
        :return: ничего (None).
        """
        try:
            if user_id not in self.__parent.temp_info.admin_vk_pages_ids:
                raise HandlerException("do_not_have_admin_rights_text")
            if len(self.__parent.temp_info.members_vk_page_ids) == 0:
                raise HandlerException("not_found_kick_all_text")

            self.__parent.messenger.send_message("start_kick_all_text", {"reply": raw_info[1]})
            self.__parent.user_manager.kick_all_users()
            self.__parent.messenger.send_message("end_kick_all_text")
            self.__main_handler_logger.debug("Все участники были успешно исключены.")
        except HandlerException as exc:
            self.__parent.messenger.send_message(str(exc), {"reply": raw_info[1]})
        else:
            self.__main_handler_logger.debug("Команда '/kick_all' успешно отработана.")

    def __kick_handler(self, raw_info: list, user_id: int) -> None:
        """
        Данный приватный метод вызывается 'main_handler' при получении команды '/kick' и
        выполняет действия по запуску соответствующего команде метода.

        :param raw_info: "сырая" информация о сообщении, полученная от 'main_handler'.
        :param user_id: ID пользователя, отправившего сообщение, полученный от 'main_handler'.
        :return: ничего (None).
        """
        try:
            if user_id not in self.__parent.temp_info.admin_vk_pages_ids:
                raise HandlerException("do_not_have_admin_rights_text")
            if raw_info[6].get("mentions") is None:
                raise HandlerException("nobody_to_kick_text")

            for user in raw_info[6]["mentions"]:
                if user in self.__parent.temp_info.admin_vk_pages_ids:
                    raise HandlerException("cannot_kick_admin_text")
                self.__parent.user_manager.kick_user(user)
        except HandlerException as exc:
            self.__parent.messenger.send_message(str(exc), {"reply": raw_info[1]})
        else:
            self.__main_handler_logger.debug("Команда '/kick' успешно отработана.")

    @ErrorNotifier.notify
    def __stop_handler(self, raw_info: list, user_id: int) -> None:
        """
        Данный приватный метод вызывается 'main_handler' при получении команды '/stop' и
        выполняет действия по запуску соответствующего команде метода.

        :param raw_info: "сырая" информация о сообщении, полученная от 'main_handler'.
        :param user_id: ID пользователя, отправившего сообщение, полученный от 'main_handler'.
        :return: ничего (None).
        """
        try:
            if user_id not in self.__parent.temp_info.admin_vk_pages_ids:
                raise HandlerException("do_not_have_admin_rights_text")
            if self.__parent.temp_info.start_function_first_start:
                raise HandlerException("quiz_already_stopped_text")

            self.__parent.temp_info.start_function_first_start = True
            self.__parent.stop_event.set()
            if self.__parent.quiz_thread.is_alive():
                self.__parent.quiz_thread.join()
            self.__main_handler_logger.debug("Метод 'quiz_mainloop' был завершен.")
            self.__parent.stop_event.clear()
        except HandlerException as exc:
            self.__parent.messenger.send_message(str(exc), {"reply": raw_info[1]})

    @ErrorNotifier.notify
    def main_handler(self, user_message: str, raw_info: list, user_id: int) -> None:
        """
        Данный метод обрабатывает текстовые сообщения от пользователей, пойманные основным
        слушателем 'main_listener'. Основная его задача - выследить команды, начинающиеся
        с '/' ('/start', '/get_chat' и т.д.) и обработать их.

        :param user_message: текст сообщения пользователя, полученного от 'main_listener'.
        :param raw_info: сырая информация о сообщении, полученная от 'main_listener'.
        :param user_id: ID страницы VK пользователя, который отправил сообщение, полученный от
        'main_listener'.
        :return: ничего (None).
        """
        self.__main_handler_logger.debug("Метод 'main_handler' запущен.")

        with self._locker:
            try:
                handlers = {
                    "/get_chat": self.__get_chat_handler,
                    "/start": self.__start_handler,
                    "/kick_all": self.__kick_all_handler,
                    "/kick": self.__kick_handler,
                    "/stop": self.__stop_handler
                }
                handlers[user_message](raw_info, user_id)
            except KeyError:
                pass

        self.__main_handler_logger.debug("Метод 'main_handler' успешно завершил работу.\n")

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

        if dict(bot_answer_data[6]).get("payload") is not None:
            if json.loads(bot_answer_data[6]["payload"]).get("keyboard") is not None:
                _current_id_of_message_question = bot_answer_data[1]

                with self._locker:
                    self.__parent.temp_info.current_id_of_latest_quiz_message = _current_id_of_message_question

                self.__bot_question_messages_handler.debug("Метод 'bot_question_messages_handler' успешно " +
                                                           "завершил работу.\n" +
                                                           f"{Consts.TAB_SPACE_11}ID последнего вопроса - " +
                                                           f"{_current_id_of_message_question}\n")
        else:
            self.__bot_question_messages_handler.debug("Метод 'bot_question_messages_handler' не распознал " +
                                                       "в сообщении вопрос.\n")

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
            try:
                current_user_id = event_data["object"]["user_id"]
                current_event_id = event_data["object"]["event_id"]
                if current_user_id in self.__parent.temp_info.admin_vk_pages_ids:
                    raise HandlerException("admin_cannot_use_text")

                if event_data["object"]["payload"].get("score") is not None:
                    score_template: str = self.__parent.messenger.template("score_template_text", SCORE=self.__parent
                                                                           .temp_info.members_scores.get(
                        str(current_user_id), 0))
                    self._vk_session.method("messages.sendMessageEventAnswer", {
                        "event_id": current_event_id,
                        "user_id": current_user_id,
                        "peer_id": Consts.PEER_ID_ADDITION_INT + self._bot_config["chat_for_work_id"],
                        "event_data": json.dumps({
                            "type": "show_snackbar",
                            "text": score_template
                        })
                    })
                    return

                current_payload = event_data["object"]["payload"]["answer"]

                self.__members_quiz_answers_handler.debug(f"Текущий ID пользователя: {current_user_id}\n" +
                                                          f"{Consts.TAB_SPACE_11}Текущий ID события: {current_event_id}\n" +
                                                          f"{Consts.TAB_SPACE_11}Текущий пэйлод: {current_payload}")

                if self.__parent.answer_block:
                    raise HandlerException("answer_blocked_text")
                if current_user_id in self.__parent.temp_info.members_answered_on_quiz:
                    raise HandlerException("already_answered_text")

                if self._bot_config["quiz_mode"] == "Score":
                    current_question: dict = self.__parent.quiz_manager.get_current_question()
                    if current_payload:
                        if str(current_user_id) not in self.__parent.temp_info.members_scores:
                            self.__parent.temp_info.members_scores.update(
                                {str(current_user_id): current_question["score"]})
                        else:
                            self.__parent.temp_info.members_scores[str(current_user_id)] = self.__parent.temp_info \
                                                                                               .members_scores.get(
                                str(current_user_id), 0) + current_question["score"]

                        self.__members_quiz_answers_handler.debug(f"Пользователю {current_user_id} успешно " +
                                                                  "начислено {current_question['score']} баллов.")
                    else:
                        if str(current_user_id) not in self.__parent.temp_info.members_scores:
                            self.__parent.temp_info.members_scores.update(
                                {str(current_user_id): -current_question["score"]})
                        else:
                            self.__parent.temp_info.members_scores[str(current_user_id)] = self.__parent.temp_info \
                                                                                               .members_scores.get(
                                str(current_user_id), 0) - current_question["score"]

                        self.__members_quiz_answers_handler.debug(f"Пользователю {current_user_id} " +
                                                                  "начислено -{current_question['score']} баллов.")

                else:
                    if current_payload:
                        self.__parent.temp_info.members_answered_on_quiz_right.append(current_user_id)
                        self.__members_quiz_answers_handler.debug(f"Пользователь {current_user_id} добавлен " +
                                                                  "в список успешно ответивших.")

                self.__parent.temp_info.members_answered_on_quiz.append(current_user_id)
                raise HandlerException("answer_got_text")

            except HandlerException as exc:
                self._vk_session.method("messages.sendMessageEventAnswer", {
                    "event_id": current_event_id,
                    "user_id": current_user_id,
                    "peer_id": Consts.PEER_ID_ADDITION_INT + self._bot_config["chat_for_work_id"],
                    "event_data": json.dumps({
                        "type": "show_snackbar",
                        "text": self.__texts_for_messages[str(exc)]
                    })
                })
                self.__members_quiz_answers_handler.debug(f"Пользователь {current_user_id} получил ответ " +
                                                          "на Callback-событие.\n")
