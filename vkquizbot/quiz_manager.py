# Package name: vkquizbot
# Module name: quiz_manager.py
# Author(s): SkyForces
# Modification date: January 2023
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
from typing import Any, Callable

# Сторонние библиотеки
import playsound

# Модули бота
from .utils import UtilsInitDefault, ErrorNotifier


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
        if self.__dump_data is not None:
            self.__parent.messenger.unpin_message()
            self.__parent.messenger.send_message("Начат процесс восстановления сеанса, подождите...",
                                                 {"empty_keyboard": True})

            self.__already_used_question_numbers, self.__question_list_to_load = self.__dump_data[1], \
                self.__dump_data[2]
            self.__current_question_number, self.__round_counter = self.__dump_data[3], self.__dump_data[4]
            self.__time_wait = self.__dump_data[5]
            self.__crash_state = True
            self.__parent.quiz_thread = threading.Thread(target=self.quiz_mainloop, daemon=True,
                                                         name="QuizMainloopThread")

            self.__parent.data_manager.rewrite_json(self.__dump_data[0], "temp_info", self.__quiz_logger)
            ErrorNotifier.remove_previous_flags()

            self.__parent.messenger.send_message("Процесс восстановления сеанса завершен.")
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
                                 f"\n{'=' * 30}[Конец логгирования]{'=' * 30}")

    @ErrorNotifier.notify
    def __save_state(self, file_name: str) -> None | list[Any]:
        """
        Данный метод загружает bin-файл с указанным названием с сериализованными данными с
        прошлого сеанса и обрабатывает его.

        Если в папке 'dump' будут найдены флаги об ошибках, то метод вернет содержимое файла,
        которое впоследствии будет использовано для восстановления состояния прошлого сеанса.

        Если в конфиге бота параметр 'Ignore_save_state' = True, то содержимое файла не будет
        возвращено даже при наличии флагов.
        Если в конфиге бота параметр 'Force_load_save_state' = True, то содержимое файла будет
        возвращено даже при отсутствии флагов.

        :param file_name: имя bin-файла, который нужно загрузить и обработать.
        :return: ничего (None) или список с полученными значениями.
        """
        if f"{file_name}.bin" in os.listdir("dump/"):
            dumped_data = self.__parent.data_manager.pickle_load(file_name)

            if self._bot_config["Ignore_save_state"]:
                return None
            if any(file.endswith(".flag") for file in os.listdir("dump/")) or self._bot_config["Force_load_save_state"]:
                return dumped_data
            return None
        return None

    def __finish_quiz(self) -> None:
        """
        Данный метод запускается при завершении викторины, определяет (В зависимости от режима бота)
        и оглашает победителя.

        :return: ничего (None)
        """
        temp_info = self.__parent.data_manager.load_json("temp_info", self.__quiz_logger)

        try:
            if self._bot_config["Quiz_mode"] == "Score":
                score_dict = temp_info["Members_scores"]
                max_score = max(score_dict.values())
                winner_id = list(score_dict.keys())[list(score_dict.values()).index(max_score)]
                winner_name = self.__parent.user_manager.get_user_name(winner_id)
                self.__parent.messenger.send_message(f"{winner_name}, поздравляем с победой в конкурсе!" +
                                                     f"\nВы набрали наибольшее количество баллов -- {max_score}!",
                                                     {"empty_keyboard": True})
            else:
                winner_name = self.__parent.user_manager.get_user_name(temp_info["Members_VK_page_IDs"][0])
                self.__parent.messenger.send_message(f"{winner_name}, поздравляем с победой в конкурсе!" +
                                                     '\nВы -- последний "выживший"!', {"empty_keyboard": True})
            if self._bot_config["Debug_mode"]:
                playsound.playsound("assets/sounds/tada.wav")
        except ValueError:
            if self._bot_config["Debug_mode"]:
                playsound.playsound("assets/sounds/exclamation.wav")
            self.__parent.messenger.send_message("А где победитель?", {"empty_keyboard": True})

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

        if len(self.__already_used_question_numbers) != len(self.__questions_list):
            if self._bot_config["Random_selection_for_quiz_questions"]:
                while not event.is_set():
                    self.__current_question_number = random.randint(0, len(self.__questions_list) - 1)

                    if self.__current_question_number in self.__already_used_question_numbers:
                        continue
                    break

            else:
                if self.__current_question_number < len(self.__questions_list) - 1:
                    self.__current_question_number += 1

            self.__already_used_question_numbers.append(self.__current_question_number)
            self.__quiz_logger.debug(f"ID выбранного вопроса: {self.__current_question_number + 1}\n")

            return True

        if self._bot_config["Quiz_mode"] != "Score":
            if self._bot_config["Debug_mode"]:
                playsound.playsound("assets/sounds/exclamation.wav")

            self.__quiz_logger.debug("Вопросы закончились. Добавьте новые вопросы в очередь.")
            self.__parent.messenger.send_message("question_queue_finish_text", {"to_admin": True})

            questions_list_modification_time = os.path.getmtime(f"data/{self.__question_list_to_load}.json")

            while not event.is_set():
                if questions_list_modification_time != os.path.getmtime(f"data/{self.__question_list_to_load}.json"):
                    break
                time.sleep(5)
        else:
            self.__finish_quiz()
            self.__parent.stop_event.set()

        time.sleep(3)
        return False

    def __quiz_question_publish(self) -> None:
        """
        Данный метод выполняет публикацию текущего вопроса викторины и его закрепление в чате.

        :return: ничего (None).
        """
        keyboard = self.__parent.messenger.keyboard_build(self.__questions_list[self.__current_question_number]
                                                          ["keyboard_config"])
        attachment = self.__parent.messenger.attachment_upload(self.__current_question_number)

        self.__parent.messenger.send_message(f"Вопрос номер {self.__round_counter}:\n" +
                                             self.__questions_list[self.__current_question_number]["message"],
                                             {"keyboard": keyboard, "attachment": attachment})
        time.sleep(5)

        temp_info = self.__parent.data_manager.load_json("temp_info", self.__quiz_logger)

        self.__parent.messenger.pin_message(int(temp_info["Current_ID_of_latest_quiz_message"]))

    def __quiz_question_countdown(self, temp_info: dict[str, dict | list | bool | int],
                                  event: threading.Event | None = None) -> bool:
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

        if self._bot_config["Quiz_mode"] == "Blitz" and len(temp_info["Members_VK_page_IDs"]) == 2:
            while not event.is_set():
                temp_blitz = self.__parent.data_manager.load_json("temp_info", self.__quiz_logger)

                if len(temp_blitz["Members_answered_on_quiz"]) == 2:
                    return True
                time.sleep(10)

        # Для быстрого вызова исключения (в целях дебаггинга).
        # if self.__current_question_number == 1:
        #     a = 4 / 0

        while True:
            if self.__time_wait > 60 * self._bot_config["Time_on_quiz_round"]:
                return True
            if event.is_set():
                return False

            time.sleep(4)
            self.__time_wait += 4

    def __quiz_iteration_init(self) -> bool:
        """
        Данный метод реализует инициализацию итерации викторины. Он определяет, может ли быть
        продолжена викторина или нет, а также в зависимости от режима работы бота выбирает
        подходящий список вопросов.

        :return: возвращает True, если итерация викторины может быть продолжена, False - если
        викторина должна быть завершена.
        """
        temp_info = self.__parent.data_manager.load_json("temp_info", self.__quiz_logger)

        if self._bot_config["Debug_mode"]:
            playsound.playsound("assets/sounds/exclamation.wav")

        if self._bot_config["Quiz_mode"] == "Blitz":
            match len(temp_info["Members_VK_page_IDs"]):
                case 2:
                    if not temp_info["Blitz_start"]:
                        self.__round_counter = 1
                        temp_info["Blitz_start"] = True

                        self.__already_used_question_numbers.clear()
                        self.__parent.messenger.send_message("Мы переходим в режим блиц-опроса!")
                        self.__parent.data_manager.rewrite_json(temp_info, "temp_info", self.__quiz_logger)

                    self.__question_list_to_load = "blitz_questions_list"
                    return True
                case 1:
                    self.__finish_quiz()
                    self.__quiz_logger.debug("Метод 'quiz_mainloop' успешно завершил работу.")
                    return False

        if self._bot_config["Quiz_mode"] != "Score":
            if len(temp_info["Members_VK_page_IDs"]) == 1:
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
        crash_temp_info = self.__parent.data_manager.load_json("temp_info")

        self.__parent.data_manager.pickle_dump("save_state", [crash_temp_info, self.__already_used_question_numbers,
                                                              self.__question_list_to_load,
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

            temp_info = self.__parent.data_manager.load_json("temp_info", self.__quiz_logger)

            if not self.__quiz_question_countdown(temp_info):
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

        temp_info = self.__parent.data_manager.load_json("temp_info", self.__quiz_logger)

        self.__parent.messenger.send_message("Время ответа на вопрос истекло!", {"empty_keyboard": True})

        if self._bot_config["Quiz_mode"] != "Score":
            members_queued_to_kick = list(set(temp_info["Members_VK_page_IDs"]).
                                          difference(temp_info["Members_answered_on_quiz_right"]))
            self.__quiz_logger.debug(f"Участники, которые будут исключены: {members_queued_to_kick}")

            if len(members_queued_to_kick) == 0:
                self.__parent.messenger.send_message(f"По итогам {self.__round_counter} раунда никто не был исключен.")
            else:
                for member_kick in members_queued_to_kick:
                    self.__parent.user_manager.kick_user(member_kick)
                self.__parent.messenger.send_message(f"По итогам {self.__round_counter} раунда был(о) исключен(о) " +
                                                     f"{len(members_queued_to_kick)} человек(а).")

        self.__parent.messenger.unpin_message()

        keyboard = self.__parent.messenger.keyboard_build(self.__questions_list[self.__current_question_number]
                                                          ["keyboard_config"], "button_answer_color")
        right_answer_index = self.__questions_list[self.__current_question_number] \
            ["keyboard_config"]["payload_list"].index({"answer": True})
        right_answer = self.__questions_list[self.__current_question_number] \
            ["keyboard_config"]["button_name"][right_answer_index]

        self.__parent.messenger.send_message(f"Верный ответ на вопрос викторины: {right_answer}",
                                             {"keyboard": keyboard})
        time.sleep(5)

        self.__round_counter += 1
        self.__time_wait = 0
        temp_info["Members_answered_on_quiz"].clear()
        self.__quiz_logger.debug("Список 'Members_answered_on_quiz' был очищен.")
        temp_info["Members_answered_on_quiz_right"].clear()
        self.__quiz_logger.debug("Список 'Members_answered_on_quiz_right' был очищен.")
        self.__parent.data_manager.rewrite_json(temp_info, "temp_info", self.__quiz_logger)
