# Package name: vkquizbot
# Module name: messenger.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Messenger, который реализует методы работы бота с сообщениями –
создание клавиатур, прикрепление вложений к сообщениям, отправка сообщений, их закрепление и т.д.

Список классов и методов:
| Messenger(UtilsInitMessage)
    Данный класс отвечает за работу функций бота, связанных с созданием и отправкой сообщений.

⌊__ attachment_upload
        Данный метод отвечает за загрузку вложений для вопросов викторины на сервера VK.

⌊__ keyboard_build
        Данный метод отвечает за построение клавиатуры и возвращение ее методу, запросившему
        создание клавиатуры.

⌊__ send_message
        Данный метод отвечает за сборку структуры сообщения и его последующую отправку.

⌊__ pin_message
        Данный метод закрепляет в беседе сообщение с указанным ID.

⌊__ unpin_message
        Данный метод открепляет сообщение в беседе.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import json
import random

# Сторонние библиотеки
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Модули бота
from .utils import UtilsInitMessage, ErrorNotifier


class Messenger(UtilsInitMessage):
    """
    Данный класс отвечает за работу функций бота, связанных с созданием и отправкой сообщений.

    Конструктор класса:
    Данный метод отвечает за первичную инициализацию объекта работы с сообщениями.
    Создает логгер для объекта работы с сообщениями, а также создает "среду" для работы с
    VK API и загружает список вопросов викторины для последующего обращения к нему.

    :param parent: Ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | attachment_upload
    | keyboard_build
    | send_message
    | pin_message
    | unpin_message
    """
    @ErrorNotifier.notify
    def __init__(self, parent) -> None:
        self.__parent = parent
        self.__messenger_logger = self.__parent.logger.get_single_logger("messenger")
        super().__init__()

        self.__messenger_logger.debug("Токен VK для работы бота получен.")
        self.__messenger_logger.debug("VK Uploader инициализирован.")
        self.__messenger_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__messenger_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                      f"\n{'=' * 30}[Конец логгирования]{'=' * 30}")

    @ErrorNotifier.notify
    def attachment_upload(self, question_number: int) -> str:
        """
        Данный метод отвечает за загрузку вложений для вопросов викторины на сервера VK и получение
        ссылок на них. На данный момент поддерживается только загрузка изображений.

        :param question_number: номер вопроса викторины, для которого нужно загрузить вложения.
        :return: строка со списком ссылок на вложения.
        """
        self.__messenger_logger.debug("Метод 'attachment_uploader' запущен.")

        temp_info = self.__parent.data_manager.load_json("temp_info", self.__messenger_logger)
        list_to_load = "questions_list" if not temp_info["Blitz_start"] else "blitz_questions_list"
        questions_list = self.__parent.data_manager.load_json(list_to_load, self.__messenger_logger)
        attachment = questions_list[question_number]["attachment"]
        attachment_to_load = str()

        for type_ in questions_list[question_number]["attach_type"]:
            match type_:
                case "photo":
                    photo_list = self._uploader.photo_messages(attachment["photo"])
                    attachment_to_load = ','.join(f"photo{item['owner_id']}_{item['id']}" for item in photo_list)

                # pylint: disable=fixme
                # TODO: Написать код для загрузки вложений следующих типов: видео, аудио, документы
                #  (Проблемы с реализацией, отложено).
                # case "audio":
                #     audio_list = list()
                #     for current_file in attachment["audio"]:
                #         audio_dict = self._uploader.audio_message(current_file, peer_id=2000000000
                #                                                   + self._bot_config["Chat_for_work_ID"])
                #         print(audio_dict)
                #         audio_list.append('audmsg{owner_id}_{id}'.format(**audio_dict["audio_message"]))
                #     attachment_to_load += ',' + ','.join(item for item in audio_list)
                # case "video":
                #     video_list = self._uploader.video(attachment["video"])
                #     attachment_to_load = ','.join('video{owner_id}_{id}'.format(**item) for item in video_list)
                # case "file":
                #     file_list = list()
                #     for current_file in attachment["file"]:
                #         file_dict = self._uploader.document(current_file, message_peer_id=2000000000 +
                #                                             self._bot_config["Chat_for_work_ID"],
                #                                             title=current_file.lstrip("Attachments/"), tags=["Bot"])
                #         print(file_dict)
                #         file_list.append('doc{owner_id}_{id}'.format(**file_dict["doc"]))
                #     attachment_to_load += ',' + ','.join(item for item in file_list)

        self.__messenger_logger.debug("Выполнение метода 'attachment_uploader' завершено. " +
                                      "Вложения успешно загружены. " +
                                      f"Тип - '{questions_list[question_number]['attach_type']}'\n")

        return attachment_to_load

    @ErrorNotifier.notify
    def keyboard_build(self, keyboard_config: dict[str, bool | list | int],
                       color_list_name: str | None = None) -> VkKeyboard | None:
        """
        Данный метод отвечает за построение клавиатуры с параметрами, указанными в конфигурации
        конкретного вопроса викторины, и возвращение ее методу, запросившему создание клавиатуры.

        :param keyboard_config: словарь из основных параметров, необходимых для построения
        клавиатуры. Данные параметры хранятся в конфигурации вопроса в словаре 'keyboard_config'.
        :param color_list_name: данный параметр указывает, какой список цветов кнопок использовать.
        По умолчанию используется список "button_color", идущий вместе с вопросом.
        :return: экземпляр класса 'VkKeyboard' или ничего (None).
        """
        self.__messenger_logger.debug("Метод 'keyboard_create' запущен.")

        current_keyboard = VkKeyboard(inline=keyboard_config["inline_mode"], one_time=keyboard_config["onetime_mode"])
        color_list = keyboard_config["button_color"] if color_list_name is None else keyboard_config[color_list_name]

        if keyboard_config["button_quantity"] != 0:
            for button in range(keyboard_config["button_quantity"]):
                match color_list[button]:
                    case "POSITIVE":
                        current_keyboard.add_callback_button(keyboard_config["button_name"][button],
                                                             VkKeyboardColor.POSITIVE,
                                                             keyboard_config["payload_list"][button])
                    case "NEGATIVE":
                        current_keyboard.add_callback_button(keyboard_config["button_name"][button],
                                                             VkKeyboardColor.NEGATIVE,
                                                             keyboard_config["payload_list"][button])
                    case "PRIMARY":
                        current_keyboard.add_callback_button(keyboard_config["button_name"][button],
                                                             VkKeyboardColor.PRIMARY,
                                                             keyboard_config["payload_list"][button])
                    case "SECONDARY":
                        current_keyboard.add_callback_button(keyboard_config["button_name"][button],
                                                             VkKeyboardColor.SECONDARY,
                                                             keyboard_config["payload_list"][button])
                if keyboard_config["keyboard_build_style"] == "per_line" \
                        and button != keyboard_config["button_quantity"] - 1:
                    current_keyboard.add_line()

            self.__messenger_logger.debug("Клавиатура создана.\n" +
                                          '\t' * 6 + f"   Inline mode = {keyboard_config['inline_mode']}, " +
                                          f"One-Time mode = {keyboard_config['onetime_mode']}\n" +
                                          '\t' * 6 + f"   Количество кнопок = {keyboard_config['button_quantity']}\n" +
                                          '\t' * 6 + "   Расположение кнопок = " +
                                                     f"{keyboard_config['keyboard_build_style']}\n" +
                                          '\t' * 6 + f"   Список имен кнопок: {keyboard_config['button_name']}\n" +
                                          '\t' * 6 + f"   Список цветов кнопок: {keyboard_config['button_color']}\n" +
                                          '\t' * 6 + f"   Список пэйлодов кнопок: {keyboard_config['payload_list']}\n")

            return current_keyboard

        return None

    @ErrorNotifier.notify
    def send_message(self, message_text: str,
                     message_data: dict[str, bool | VkKeyboard | str] | None = None) -> None:
        """
        Данный метод отвечает за сборку структуры сообщения и его последующую отправку.

        :param message_text: текст, который нужно отправить. Если вместо текста указать заголовок
        сообщения из 'texts_for_questions.json', то будет отправлен текст сообщения, связанный
        с этим заголовком.
        :param message_data: словарь со всеми дополнительными параметрами для сообщения по типу
        вложений и клавиатуры.
        Параметры: 'attachment' - список ссылок на вложения, 'keyboard' - объект клавиатуры для
        отправки, 'empty_keyboard' (bool) - отправка пустой клавиатуры,
        'to_admin' (bool) - указывает, что сообщение должно быть отправлено в ЛС
        администратору бота.
        :return: ничего (None).
        """
        self.__messenger_logger.debug("Метод 'send_message' запущен.")

        if message_data is None:
            message_data = {}

        with self._locker:
            message_texts = self.__parent.data_manager.load_json("texts_for_messages", self.__messenger_logger)

            if message_text in message_texts:
                message_text = message_texts[f"{message_text}"]

        message_data_dict = {
                    "peer_id": 2000000000 + self._bot_config["Chat_for_work_ID"],
                    "chat_id": self._bot_config["Chat_for_work_ID"],
                    "message": message_text,
                    "random_id": random.randint(-30000000, 300000000),
                    "payload": json.dumps({
                        "is_bot": True
                    }),
                    "attachment": None,
                    "keyboard": None
                }

        if message_data.get("empty_keyboard") is not None:
            if message_data["empty_keyboard"]:
                message_data_dict["keyboard"] = VkKeyboard.get_empty_keyboard()

                self.__messenger_logger.debug("Будет отправлено сообщение с пустой клавиатурой.")

        if message_data.get("keyboard") is not None:
            message_data_dict["keyboard"] = message_data["keyboard"].get_keyboard()

            self.__messenger_logger.debug("Будет отправлено сообщение с клавиатурой.")

        if message_data.get("attachment") is not None:
            message_data_dict["attachment"] = message_data["attachment"]

            self.__messenger_logger.debug("Будет отправлено сообщение с вложением.")

        if message_data.get("to_admin") is not None:
            if message_data["to_admin"]:
                message_data_dict.pop("chat_id")
                message_data_dict["peer_id"] = self._bot_config["Lead_Admin_VK_ID"]
                message_data_dict["user_id"] = self._bot_config["Lead_Admin_VK_ID"]

        self._vk_session.method("messages.send", message_data_dict)
        self.__messenger_logger.debug("Сообщение с текстом '{}' отправлено.".format(message_text.replace('\n', ' ')) +
                                      "\n")

    @ErrorNotifier.notify
    def pin_message(self, message_id: int) -> None:
        """
        Данный метод закрепляет в беседе сообщение с указанным ID.

        :param message_id: ID сообщения, которое надо закрепить.
        :return: ничего (None).
        """
        self.__messenger_logger.debug("Метод 'pin_message' запущен.")

        self._vk_session.method("messages.pin", {
            "peer_id": 2000000000 + self._bot_config["Chat_for_work_ID"],
            "message_id": message_id
        })

        self.__messenger_logger.debug(f"Сообщение с ID {message_id} Было закреплено.")

    @ErrorNotifier.notify
    def unpin_message(self) -> None:
        """
        Данный метод открепляет сообщение в беседе.

        :return: ничего (None).
        """
        self.__messenger_logger.debug("Метод 'unpin_message' запущен.")

        self._vk_session.method("messages.unpin", {
            "peer_id": 2000000000 + self._bot_config["Chat_for_work_ID"]
        })

        self.__messenger_logger.debug("Сообщение было откреплено.")
