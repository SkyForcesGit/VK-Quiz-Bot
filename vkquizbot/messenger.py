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

⌊__ template
        Данный метод осуществляет функцию подстановки передаваемых значений в выбранное
        шаблонное сообщение.

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
import re

# Сторонние библиотеки
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Модули бота
from .utils import UtilsInitMessage, ErrorNotifier
from .consts import Consts


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
    | template
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
                                      Consts.END_OF_LOGS_LINE)

    @ErrorNotifier.notify
    def attachment_upload(self, question_number: int) -> str:
        """
        Данный метод отвечает за загрузку вложений для вопросов викторины на сервера VK и получение
        ссылок на них. На данный момент поддерживается только загрузка изображений.

        :param question_number: номер вопроса викторины, для которого нужно загрузить вложения.
        :return: строка со списком ссылок на вложения.
        """
        self.__messenger_logger.debug("Метод 'attachment_uploader' запущен.")

        list_to_load = "questions_list" if not self.__parent.temp_info.blitz_start else "blitz_questions_list"
        questions_list = self.__parent.data_manager.load_json(list_to_load, self.__messenger_logger)
        attachment = questions_list[question_number]["attachment"]
        attachment_to_load = str()

        for type_ in questions_list[question_number]["attach_type"]:
            match type_:
                case "photo":
                    photo_list = self._uploader.photo_messages(attachment["photo"])
                    attachment_to_load = ','.join(f"photo{item['owner_id']}_{item['id']}" for item in photo_list)

        self.__messenger_logger.debug("Выполнение метода 'attachment_uploader' завершено. " +
                                      "Вложения успешно загружены. " +
                                      f"Тип - '{questions_list[question_number]['attach_type']}'\n")

        return attachment_to_load

    @ErrorNotifier.notify
    def template(self, text: str, **kwargs) -> str:
        """
        Данный метод осуществляет функцию подстановки передаваемых значений в выбранное
        шаблонное сообщение и возвращает уже отформатированный текст.

        :param text: заголовок для сообщения из 'texts_for_questions.json', с которым связан текст
        необходимого сообщения.
        :param kwargs: группа именованных аргументов, передающая в метод необходимые данные для
        подстановки в поля сообщения. Если для поля не будет найдено ни одного соответствия среди
        имен аргументов, то поле заполнится знаками вопроса.
        :return: строка с отформатированным текстом.
        """
        def check(word):
            return "?" * (len(word) - 2) if re.match(r"[A-Z]?[A-Z0-9_]+", word) else word

        text_msg = self.__parent.texts_for_msgs[text]
        output = []

        for part in text_msg.split(" "):
            if re.search(fr"{Consts.VAR_BORDER}[A-Z]?[A-Z0-9_]+{Consts.VAR_BORDER}", part):
                if any(x in kwargs for x in part.split(Consts.VAR_BORDER)):
                    part = ''.join(str(kwargs[x]) if x in kwargs else check(x) for x in part.split(Consts.VAR_BORDER))
            else:
                part = ''.join(str(check(x)) for x in part.split(Consts.VAR_BORDER))
            output.append(part)

        return ' '.join(output)

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
        names, colors, payloads = [], [], []
        buttons = keyboard_config["buttons"]

        for button in range(len(keyboard_config["buttons"])):
            if color_list_name:
                if buttons[button].get(color_list_name) is not None:
                    color = buttons[button][color_list_name]
                else:
                    color = "POSITIVE" if buttons[button]["payload"] else "PRIMARY"
            else:
                color = buttons[button]["color"] if buttons[button].get("color") else "PRIMARY"

            vk_keyboard_color = getattr(VkKeyboardColor, color)
            name = keyboard_config["buttons"][button]["name"]
            payload = keyboard_config["buttons"][button]["payload"]

            current_keyboard.add_callback_button(name, vk_keyboard_color, {"answer": payload})

            if keyboard_config["keyboard_build_style"] == "per_line" \
                    and button != len(keyboard_config["buttons"]) - 1:
                current_keyboard.add_line()

            names.append(name)
            colors.append(color)
            payloads.append(payload)

        self.__messenger_logger.debug("Клавиатура создана.\n" +
                                      f"{Consts.TAB_SPACE_6}Inline mode = {keyboard_config['inline_mode']},\n" +
                                      f"{Consts.TAB_SPACE_6}One-Time mode = {keyboard_config['onetime_mode']},\n" +
                                      f"{Consts.TAB_SPACE_6}Количество кнопок = {len(keyboard_config['buttons'])},\n" +
                                      f"{Consts.TAB_SPACE_6}Расположение кнопок = " +
                                      f"{keyboard_config['keyboard_build_style']},\n" +
                                      f"{Consts.TAB_SPACE_6}Список имен кнопок: {names},\n" +
                                      f"{Consts.TAB_SPACE_6}Список цветов кнопок: {colors},\n" +
                                      f"{Consts.TAB_SPACE_6}Список пэйлодов кнопок: {payloads}\n")

        return current_keyboard

    @ErrorNotifier.notify
    def send_message(self, message_text: str,
                     message_data: dict[str, bool | VkKeyboard | str] | None = None) -> None:
        """
        Данный метод отвечает за сборку структуры сообщения и его последующую отправку.

        Параметры 'message_data': 'attachment' - список ссылок на вложения, 'keyboard' - объект
        клавиатуры для отправки, 'empty_keyboard' (bool) - отправка пустой клавиатуры,
        'to_admin' (bool) - указывает, что сообщение должно быть отправлено в ЛС
        администратору бота, 'reply' - ID сообщения, на которое нужно ответить.

        :param message_text: текст, который нужно отправить. Если вместо текста указать заголовок
        сообщения из 'texts_for_questions.json', то будет отправлен текст сообщения, связанный
        с этим заголовком.
        :param message_data: словарь со всеми дополнительными параметрами для сообщения по типу
        вложений и клавиатуры.
        :return: ничего (None).
        """
        self.__messenger_logger.debug("Метод 'send_message' запущен.")

        if message_data is None:
            message_data = {}

        with self._locker:
            message_texts = self.__parent.texts_for_msgs

            if message_text in message_texts:
                message_text = message_texts[message_text]

        message_data_dict = {
                    "peer_id": Consts.PEER_ID_ADDITION_INT + self._bot_config["chat_for_work_id"],
                    "chat_id": self._bot_config["chat_for_work_id"],
                    "message": message_text,
                    "random_id": random.randint(Consts.RANDINT_BOTTOM_BOUND, Consts.RANDINT_TOP_BOUND),
                    "payload": json.dumps({
                        "is_bot": True
                    }),
                    "attachment": None,
                    "keyboard": None
                }

        if message_data.get("empty_keyboard") is not None:
            message_data_dict["keyboard"] = VkKeyboard.get_empty_keyboard()

            self.__messenger_logger.debug("Будет отправлено сообщение с пустой клавиатурой.")

        if message_data.get("keyboard") is not None:
            message_data_dict["keyboard"] = message_data["keyboard"].get_keyboard()

            self.__messenger_logger.debug("Будет отправлено сообщение с клавиатурой.")

        if message_data.get("attachment") is not None:
            message_data_dict["attachment"] = message_data["attachment"]

            self.__messenger_logger.debug("Будет отправлено сообщение с вложением.")

        if message_data.get("reply") is not None:
            message_data_dict["reply_to"] = message_data["reply"]

            self.__messenger_logger.debug("Будет отправлено сообщение с ответом.")

        if message_data.get("to_admin") is not None:
            message_data_dict.pop("chat_id")
            message_data_dict["peer_id"] = self._bot_config["lead_admin_vk_id"]
            message_data_dict["user_id"] = self._bot_config["lead_admin_vk_id"]

        self._vk_session.method("messages.send", message_data_dict)
        self.__messenger_logger.debug("Сообщение с текстом '{}' отправлено.\n".format(message_text.replace('\n', ' ')))

    @ErrorNotifier.notify
    def pin_message(self, message_id: int) -> None:
        """
        Данный метод закрепляет в беседе сообщение с указанным ID.

        :param message_id: ID сообщения, которое надо закрепить.
        :return: ничего (None).
        """
        self.__messenger_logger.debug("Метод 'pin_message' запущен.")

        self._vk_session.method("messages.pin", {
            "peer_id": Consts.PEER_ID_ADDITION_INT + self._bot_config["chat_for_work_id"],
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
            "peer_id": Consts.PEER_ID_ADDITION_INT + self._bot_config["chat_for_work_id"]
        })

        self.__messenger_logger.debug("Сообщение было откреплено.")
