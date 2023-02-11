# Package name: vkquizbot
# Module name: quiz_manager.py
# Author(s): SkyForces
# Modification date: February 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс QuizManager, который реализует алгоритм бота, отвечающий за
проведение викторины. К этому алгоритму относится составление и отправка вопросов, исключение
участников, определение победителя и т.д.

Список классов и методов:
| QuizManager(UtilsInitDefault)
    Данный класс отвечает за работу основных функций бота, связанных с процессом
    проведения викторины.

⌊__ __save_state [PRIVATE]
        Данный метод загружает bin-файл с указанным названием и обрабатывает его.

⌊__ __finish_quiz [PRIVATE]
        Данный метод запускается при завершении викторины, определяет и оглашает победителя.

⌊__ __question_select [PRIVATE]
        Данный метод осуществляет процесс выбора вопроса из общего списка вопросов.

⌊__ __quiz_question_publish [PRIVATE]
        Данный метод выполняет публикацию текущего вопроса викторины и его закрепление в чате.

⌊__ __quiz_question_countdown [PRIVATE]
        Данный метод осуществляет отсчет времени до конца раунда.

⌊__ __quiz_iteration_init [PRIVATE]
        Данный метод реализует инициализацию итерации викторины.

⌊__ _save_state_create [PROTECTED]
        Данный метод инициирует процесс создания точки восстановления бота.

⌊__ quiz_mainloop
        Основной метод викторины, отвечающий почти за почти все ее функции.

⌊__ __end_of_time_handler [PRIVATE]
        Данный метод запускается после окончания времени раунда и осуществляет операции,
        необходимые для корректного завершения итерации викторины.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import time
import random
import os
import threading
from datetime import datetime
from typing import Any, Callable

# Сторонние библиотеки
import playsound

# Модули бота
from .utils import UtilsInitDefault, ErrorNotifier
from .consts import Consts


# pylint: disable=too-many-instance-attributes
class QuizManager(UtilsInitDefault):
    """
    Данный класс отвечает за работу основных функций бота, связанных с процессом
    проведения викторины. Конфигурация для викторины хранится в 'bot_config.json'.

    Параметры: 'Mode' - режим работы викторины, режим с блиц-опросом, с подсчетом очков или
    стандартный режим ('Blitz', 'Score', 'Normal'),
    Random_selection_for_questions' (bool) - определяет, выбираются ли вопросы рандомно
    из списка или нет.

    Конструктор класса:
    Данный метод отвечает за первичную инициализацию объекта викторины.
    Создает логгер для учета работы объекта викторины, а также "среду" для работы с
    VK API. Более того, метод может запускать систему восстановления прошлого сеанса при
    необходимости.

    :param parent: ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | quiz_mainloop
    | save_state_create
    """

    @ErrorNotifier.notify
    def __init__(self, parent) -> None:
        self.__parent = parent
        self.__quiz_logger = self.__parent.logger.get_single_logger("quiz")
        self.__questions_list = []
        super().__init__()

        self.__dump_data = self.__save_state("save_state")
        self.__seed = int(datetime.now().timestamp()) if self._bot_config["seed"] is None else self._bot_config["seed"]

        if self.__dump_data is not None:
            self.__parent.messenger.unpin_message()
            self.__parent.messenger.send_message("recovery_start_text", {"empty_keyboard": True})

            self.__question_list_to_load, self.__already_used_question_numbers = self.__dump_data[1], \
                self.__dump_data[2]
            self.__current_question_number, self.__round_counter = self.__dump_data[3], self.__dump_data[4]
            self.__time_wait = self.__dump_data[5]
            self.__crash_state = True
            self.__parent.quiz_thread = threading.Thread(target=self.quiz_mainloop, daemon=True,
                                                         name="QuizMainloopThread")
            self.__parent.temp_info = self.__dump_data[0]

            ErrorNotifier.remove_previous_flags()
            self.__parent.messenger.send_message("recovery_finish_text")
            self.__parent.quiz_thread.start()
        else:
            self.__already_used_question_numbers = []
            self.__question_list_to_load = None
            self.__crash_state = False
            self.__current_question_number = -1
            self.__round_counter = 1
            self.__time_wait = 0

        self.__quiz_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__quiz_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                 Consts.END_OF_LOGS_LINE)

    @ErrorNotifier.notify
    def __save_state(self, file_name: str) -> None | list[Any]:
        """
        Данный метод загружает bin-файл с указанным названием с сериализованными данными с
        прошлого сеанса и обрабатывает его.

        Если в папке 'dump' будут найдены флаги об ошибках, то метод вернет содержимое файла,
        которое впоследствии будет использовано для восстановления состояния прошлого сеанса.

        Если в конфиге бота параметр 'ignore_save_state' = True, то содержимое файла не будет
        возвращено даже при наличии флагов.
        Если в конфиге бота параметр 'force_load_save_state' = True, то содержимое файла будет
        возвращено даже при отсутствии флагов.

        :param file_name: имя bin-файла, который нужно загрузить и обработать.
        :return: ничего (None) или список с полученными значениями.
        """
        if f"{file_name}.bin" in os.listdir("dump/"):
            dumped_data = self.__parent.data_manager.pickle_load(file_name)

            if self._bot_config["ignore_save_state"]:
                return None

            if any(file.endswith(".flag") for file in os.listdir("dump/")) or self._bot_config["force_load_save_state"]:
                return dumped_data

            return None

        return None

    def __finish_quiz(self) -> None:
        """
        Данный метод запускается при завершении викторины, определяет (В зависимости от режима бота)
        и оглашает победителя.

        :return: ничего (None)
        """
        try:
            if self._bot_config["quiz_mode"] == "Score":
                score_dict = self.__parent.temp_info.members_scores
                max_score, min_score = max(score_dict.values()), min(score_dict.values())
                winner_id = list(score_dict.keys())[list(score_dict.values()).index(max_score)]
                min_score_member_id = list(score_dict.keys())[list(score_dict.values()).index(min_score)]
                winner_name = self.__parent.user_manager.get_name(int(winner_id))
                min_score_member = self.__parent.user_manager.get_name(int(min_score_member_id))
                template_1 = self.__parent.messenger.template("winner_score_text", WINNER_NAME=winner_name,
                                                              MAX_SCORE=max_score, MIN_SCORE=min_score,
                                                              MIN_SCORE_MEMBER=min_score_member)

                self.__parent.messenger.send_message(template_1, {"empty_keyboard": True})
            else:
                winner_name = self.__parent.user_manager.get_name(self.__parent.temp_info["Members_VK_page_IDs"][0])
                template_2 = self.__parent.messenger.template("winner_score_text", WINNER_NAME=winner_name)

                self.__parent.messenger.send_message(template_2, {"empty_keyboard": True})
            if self._bot_config["debug_mode"]:
                playsound.playsound("assets/sounds/tada.wav")
        except ValueError:
            if self._bot_config["debug_mode"]:
                playsound.playsound("assets/sounds/exclamation.wav")
            self.__parent.messenger.send_message("winner_do_not_found_text", {"empty_keyboard": True})

    def __question_select(self, event: threading.Event | None = None) -> bool:
        """
        Данный метод осуществляет процесс выбора вопроса из общего списка вопросов.

        :param event: ожидается экземпляр класса threading.Event.
        :return: True - если вопрос был выбран, False - если вопрос не был выбран и нужна
        следующая итерация.
        """
        if event is None:
            event = self.__parent.stop_event

        if self.__crash_state:
            self.__crash_state = False
            return True

        rand_gen = random.Random(self.__seed)

        if len(self.__already_used_question_numbers) != len(self.__questions_list):
            if self._bot_config["random_selection_for_quiz_questions"]:
                while not event.is_set():
                    self.__current_question_number = rand_gen.randint(0, len(self.__questions_list) - 1)

                    if self.__current_question_number in self.__already_used_question_numbers:
                        continue
                    break
            else:
                if self.__current_question_number < len(self.__questions_list) - 1:
                    self.__current_question_number += 1

            self.__already_used_question_numbers.append(self.__current_question_number)
            self.__quiz_logger.debug(f"ID выбранного вопроса: {self.__current_question_number + 1}\n")
            return True

        if self._bot_config["quiz_mode"] != "Score":
            if self._bot_config["debug_mode"]:
                playsound.playsound("assets/sounds/exclamation.wav")

            self.__quiz_logger.debug("Вопросы закончились. Добавьте новые вопросы в очередь.")
            self.__parent.messenger.send_message("question_queue_finish_text", {"to_admin": True})

            questions_list_modification_time = os.path.getmtime(f"data/{self.__question_list_to_load}.json")
            while not event.is_set():
                if questions_list_modification_time != os.path.getmtime(f"data/{self.__question_list_to_load}.json"):
                    break
                time.sleep(Consts.TIME_DELAY_5)
        else:
            self.__finish_quiz()
            self.__parent.stop_event.set()

        time.sleep(Consts.TIME_DELAY_5)
        return False

    def __quiz_question_publish(self) -> None:
        """
        Данный метод выполняет публикацию текущего вопроса викторины и его закрепление в чате.

        :return: ничего (None).
        """
        keyboard = self.__parent.messenger.keyboard_build(self.__questions_list[self.__current_question_number]
                                                          ["keyboard_config"])
        attachment = self.__parent.messenger.attachment_upload(self.__current_question_number)
        template = self.__parent.messenger.template("question_text", ROUND_COUNTER=self.__round_counter)

        self.__parent.messenger.send_message(template + self.__questions_list[self.__current_question_number] \
                                             ["message"], {"keyboard": keyboard, "attachment": attachment})
        time.sleep(Consts.TIME_DELAY_5)

        self.__parent.messenger.pin_message(int(self.__parent.temp_info.current_id_of_latest_quiz_message))

    def __quiz_question_countdown(self, temp_info, event: threading.Event | None = None) -> bool:
        """
        Данный метод осуществляет отсчет времени до конца раунда. В режиме блиц-опроса ожидает,
        пока ответят оба участника, а затем завершается.

        :param temp_info: временные данные в формате словаря, загруженные из JSON.
        :param event: ожидается экземпляр класса threading.Event.
        :return: возвращает True, если метод завершился штатным образом, False - если метод был
        прерван запросом на остановку потока викторины.
        """
        if event is None:
            event = self.__parent.stop_event

        if self._bot_config["quiz_mode"] == "Blitz" \
                and len(temp_info.members_vk_page_ids) == Consts.MEMBER_QUANT_TO_KEEP_BLITZ:
            while not event.is_set():
                temp_blitz = self.__parent.temp_info
                if len(temp_blitz.members_answered_on_quiz) == Consts.MEMBER_QUANT_TO_KEEP_BLITZ:
                    return True

                time.sleep(Consts.TIME_DELAY_10)

        while True:
            if self.__time_wait > Consts.QUIZ_TIME_DELAY_SAMPLE * self._bot_config["time_on_quiz_round"]:
                return True

            if event.is_set():
                return False

            time.sleep(Consts.TIME_DELAY_5)
            self.__time_wait += Consts.TIME_DELAY_5

    def __quiz_iteration_init(self) -> bool:
        """
        Данный метод реализует инициализацию итерации викторины. Он определяет, может ли быть
        продолжена викторина или нет, а также в зависимости от режима работы бота выбирает
        подходящий список вопросов.

        :return: возвращает True, если итерация викторины может быть продолжена, False - если
        викторина должна быть завершена.
        """
        if self._bot_config["debug_mode"]:
            playsound.playsound("assets/sounds/exclamation.wav")

        if self._bot_config["quiz_mode"] == "Blitz":
            match len(self.__parent.temp_info.members_vk_page_ids):
                case Consts.MEMBER_QUANT_TO_KEEP_BLITZ:
                    if not self.__parent.temp_info.blitz_start:
                        self.__round_counter = 1
                        self.__parent.temp_info.blitz_start = True
                        self.__already_used_question_numbers.clear()
                        self.__parent.messenger.send_message("blitz_quiz_start_text")

                    self.__question_list_to_load = "blitz_questions_list"
                    return True

                case Consts.MEMBERS_TO_FINISH_BOUND:
                    self.__finish_quiz()
                    self.__quiz_logger.debug("Метод 'quiz_mainloop' успешно завершил работу.")
                    return False

        if self._bot_config["quiz_mode"] != "Score":
            if len(self.__parent.temp_info["Members_VK_page_IDs"]) == Consts.MEMBERS_TO_FINISH_BOUND:
                self.__finish_quiz()
                self.__quiz_logger.debug("Метод 'quiz_mainloop' успешно завершил работу.")
                return False

        self.__question_list_to_load = "questions_list"
        return True

    def _save_state_create(self) -> None:
        """
        Данный метод инициирует процесс создания точки восстановления бота, которая может быть
        использована при следующей загрузке программы.

        :return: ничего (None).
        """
        self.__parent.data_manager.pickle_dump("save_state", [self.__parent.temp_info, self.__question_list_to_load,
                                                              self.__already_used_question_numbers,
                                                              self.__current_question_number, self.__round_counter,
                                                              self.__time_wait])

    # pylint: disable=missing-function-docstring
    @property
    def save_state_create(self) -> Callable[[], Any]:
        return self._save_state_create

    @ErrorNotifier.notify
    def quiz_mainloop(self, event: threading.Event | None = None) -> None:
        """
        Основной метод викторины, отвечающий почти за почти все ее функции. Инициирует выбор
        вопроса и его отправку, загрузку вложений, формирование клавиатуры, отправку сообщений,
        исключение участников, завершение викторины.

        :param event: ожидается экземпляр класса threading.Event.
        :return: ничего (None).
        """
        if event is None:
            event = self.__parent.stop_event

        self.__quiz_logger.debug("Метод 'quiz_mainloop' запущен.")
        self.__quiz_logger.debug(f"Сид викторины - {self.__seed}")

        if self.__crash_state:
            pass
        else:
            self.__parent.messenger.send_message("start_command_text")

        threading.Thread(target=self.__parent.listener.members_quiz_answers_listener,
                         name="MembersQuizAnswersListenerThread", daemon=True).start()

        while not event.is_set():
            self.__quiz_logger.debug("Итерация метода 'quiz_mainloop' начата.")

            if not self.__quiz_iteration_init():
                return None

            self.__questions_list = self.__parent.data_manager.load_json(self.__question_list_to_load,
                                                                         self.__quiz_logger)
            if not self.__question_select():
                continue
            self.__quiz_question_publish()

            self.__parent.answer_block = False

            if not self.__quiz_question_countdown(self.__parent.temp_info):
                self.__parent.messenger.send_message("stop_quiz_text")
                return None

            self.__parent.answer_block = True
            self.__end_of_time_handler()
            self.__quiz_logger.debug("Итерация метода 'quiz_mainloop' завершена.\n")

    def __end_of_time_handler(self) -> None:
        """
        Данный метод запускается после окончания времени раунда и осуществляет операции, необходимые
        для корректного завершения итерации викторины. Он исключает участников, ответивших неверно
        (В зависимости от режима работы), показывает правильный ответ и очищает некоторые
        временные данные.

        :return: ничего (None).
        """
        self.__quiz_logger.debug("Метод 'end_of_time_kicker' запущен.")
        self.__parent.messenger.send_message("answer_time_over_text", {"empty_keyboard": True})

        if self._bot_config["quiz_mode"] != "Score":
            members_queued_to_kick = list(set(self.__parent.temp_info.members_vk_page_ids).
                                          difference(self.__parent.temp_info.members_answered_on_quiz_right))
            self.__quiz_logger.debug(f"Участники, которые будут исключены: {members_queued_to_kick}")

            if len(members_queued_to_kick) == 0:
                template_1 = self.__parent.messenger.template("nobody_was_kicked_text",
                                                              ROUND_COUNTER=self.__round_counter)
                self.__parent.messenger.send_message(template_1)
            else:
                for member_kick in members_queued_to_kick:
                    self.__parent.user_manager.kick_user(member_kick)
                template_2 = self.__parent.messenger.template("nobody_was_kicked_text",
                                                              COUNT_MEMBERS_TO_KICK=len(members_queued_to_kick),
                                                              ROUND_COUNTER=self.__round_counter)
                self.__parent.messenger.send_message(template_2)

        self.__parent.messenger.unpin_message()
        keyboard = self.__parent.messenger.keyboard_build(self.__questions_list[self.__current_question_number]
                                                          ["keyboard_config"], "answer_color")
        current_question_answers = self.__questions_list[self.__current_question_number]["keyboard_config"]["buttons"]
        right_answers = [item["name"] for item in current_question_answers if item["payload"]]
        template_3 = self.__parent.messenger.template("right_answer_text", RIGHT_ANSWERS=', '.join(right_answers))

        self.__parent.messenger.send_message(template_3, {"keyboard": keyboard})
        time.sleep(Consts.TIME_DELAY_5)

        self.__round_counter += 1
        self.__time_wait = 0
        self.__parent.temp_info.members_answered_on_quiz.clear()
        self.__quiz_logger.debug("Список 'Members_answered_on_quiz' был очищен.")
        self.__parent.temp_info.members_answered_on_quiz_right.clear()
        self.__quiz_logger.debug("Список 'Members_answered_on_quiz_right' был очищен.")
