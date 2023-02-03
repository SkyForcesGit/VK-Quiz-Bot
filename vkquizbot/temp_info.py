# Package name: vkquizbot
# Module name: temp_info.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс TempInfo, который используется для хранения временных данных бота.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""

# Стандартная библиотека
import dataclasses


# pylint: disable=too-many-instance-attributes
@dataclasses.dataclass
class TempInfo:
    """
    Данный класс хранит в себе атрибуты, в которых сохраняются временные данные бота.

    Конструктор класса:
    Данный метод задает все основные поля класса, в которых впоследствии сохраняются данные.

    Список доступных атрибутов класса:
    | members_vk_page_ids
    | admin_vk_pages_ids
    | members_answered_on_quiz_right
    | members_answered_on_quiz
    | members_scores
    | get_chat_first_start
    | start_function_first_start
    | blitz_start
    | current_id_of_latest_quiz_message
    """
    members_vk_page_ids: list = dataclasses.field(default_factory=list)
    admin_vk_pages_ids: list = dataclasses.field(default_factory=list)
    members_answered_on_quiz_right: list = dataclasses.field(default_factory=list)
    members_answered_on_quiz: list = dataclasses.field(default_factory=list)
    members_scores: dict = dataclasses.field(default_factory=dict)
    get_chat_first_start: bool = True
    start_function_first_start: bool = True
    blitz_start: bool = False
    current_id_of_latest_quiz_message: int = 0
