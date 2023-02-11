# Package name: vkquizbot
# Module name: user_manager.py
# Author(s): SkyForces
# Modification date: February 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс UserManager, который реализует методы работы бота с
пользователями: получение информации о них, исключение их из беседы и т.д.

Список классов и методов:
| UserManager(UtilsInitVKAPI)
    Данный класс отвечает за работу функций бота, связанных с манипуляциями участниками беседы.

⌊__ get_chat
        Данный метод отвечает за сбор ID страниц VK всех участников беседы.

⌊__ kick_user
        Данный метод исключает участника с указанным ID страницы VK из беседы.

⌊__ get_name
        Данный метод получает и возвращает имя пользователя с указанным ID страницы VK.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Модули бота
from .utils import UtilsInitVKAPI, ErrorNotifier
from .consts import Consts


class UserManager(UtilsInitVKAPI):
    """
    Данный класс отвечает за работу функций бота, связанных с манипуляциями участниками беседы:
    исключение участников, получение о них различной информации и т.д.

    Конструктор класса:
    Данный метод отвечает за первичную инициализацию объекта работы с пользователями.
    Создает логгер для объекта работы с пользователями, а также создает "среду" для работы с
    VK API.

    :param parent: ссылка на экземпляр родительского класса BotCore.

    Список публичных методов:
    | get_chat
    | kick_user
    | get_name
    """
    @ErrorNotifier.notify
    def __init__(self, parent) -> None:
        self.__parent = parent
        self.__user_manager_logger = self.__parent.logger.get_single_logger("user_manager")
        super().__init__()

        self.__user_manager_logger.debug("Токен VK для работы бота получен.")
        self.__user_manager_logger.debug(f"Экземпляр класса {self.__class__.__name__} успешно создан.\n")

    def __del__(self) -> None:
        """
        Метод добавляет запись в лог об уничтожении объекта сборщиком мусора.

        :return: ничего (None).
        """
        self.__user_manager_logger.debug(f"Экземпляр класса {self.__class__.__name__} удален сборщиком мусора." +
                                         Consts.END_OF_LOGS_LINE)

    @ErrorNotifier.notify
    def get_chat(self, raw_info: list) -> None:
        """
        Данный метод отвечает за сбор ID страниц VK всех участников беседы. Также определяет
        администраторов беседы и заносит их в отдельный список.

        :param raw_info: сырая информация о сообщении, полученная от 'main_handler'. Используется
        для того, чтобы бот знал, на чье сообщение отвечать.
        :return: ничего (None).
        """
        self.__user_manager_logger.debug("Метод 'get_chat' запущен.")

        with self._locker:
            temp_info = self.__parent.temp_info
            chat_info_members = self._vk_session.method("messages.getConversationMembers", {
                "peer_id": Consts.PEER_ID_ADDITION_INT + self._bot_config["chat_for_work_id"]
            })
            chat_info_count = chat_info_members['count']
            chat_info_items = chat_info_members['items']

            for member in range(chat_info_count):
                if dict(chat_info_items[member]).get("is_admin") is not None:
                    adm_id = chat_info_items[member]["member_id"]
                    if adm_id in temp_info.admin_vk_pages_ids:
                        continue
                    temp_info.admin_vk_pages_ids.append(adm_id)
                else:
                    user_id = chat_info_items[member]["member_id"]
                    if user_id in temp_info.members_vk_page_ids:
                        continue
                    temp_info.members_vk_page_ids.append(user_id)

            self.__parent.temp_info = temp_info

        self.__user_manager_logger.debug("Сбор ID пользователей беседы завершен.\n" +
                                         f"{Consts.TAB_SPACE_6}ID пользователей: {temp_info.members_vk_page_ids}\n" +
                                         f"{Consts.TAB_SPACE_6}ID администраторов: {temp_info.admin_vk_pages_ids}\n")

        if self.__parent.quiz_thread.is_alive():
            self.__parent.messenger.send_message("get_chat_complete_text", {"reply": raw_info[1]})
        else:
            self.__parent.messenger.send_message("get_chat_complete_text", {"empty_keyboard": True,
                                                                            "reply": raw_info[1]})

    @ErrorNotifier.notify
    def get_name(self, user_id: int) -> str:
        """
        Данный метод получает и возвращает имя пользователя с указанным ID страницы VK.

        :return: строку с именем пользователя в формате "[фамилия] [имя]".
        """
        self.__user_manager_logger.debug("Метод 'get_user_name' запущен.")

        user_info = self._vk_session.method("users.get", {
            "user_ids": user_id
        })
        user_name = [f"{item['first_name']} {item['last_name']}" for item in user_info][0]

        self.__user_manager_logger.debug("Метод 'get_user_name' успешно получил имя пользователя.")

        return user_name

    @ErrorNotifier.notify
    def kick_all_users(self) -> None:
        """
        Данный метод исключает всех пользователей (кроме администраторов) из беседы.

        :return: ничего (None).
        """
        self.__user_manager_logger.debug("Метод 'kick_all_users' запущен.")

        for user_id in self.__parent.temp_info.members_vk_page_ids:
            self.kick_user(user_id)

        self.__user_manager_logger.debug("Метод 'kick_all_users' успешно завершил работу.")

    @ErrorNotifier.notify
    def kick_user(self, member_id: int) -> None:
        """
        Данный метод исключает участника с указанным ID страницы VK из беседы.

        :param member_id: ID страницы VK участника, которого нужно исключить.
        :return: ничего (None).
        """
        self.__user_manager_logger.debug("Метод 'kick_user' запущен.")

        self.__parent.temp_info.members_vk_page_ids.remove(member_id)
        self._vk_session.method("messages.removeChatUser", {
            "chat_id": self._bot_config["chat_for_work_id"],
            "user_id": member_id,
            "member_id": member_id
        })

        self.__user_manager_logger.debug(f"Участник с ID {member_id} был исключен.")
