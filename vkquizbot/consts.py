# Package name: vkquizbot
# Module name: consts.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный модуль предоставляет класс Consts, в котором хранятся все основные константы
приложения.

Подробную информацию о методах и классах ищите в документации к непосредственно им.
"""


# pylint: disable=too-few-public-methods
class Consts:
    """
    Данный класс хранит в себе основные константы, необходимые для работы приложения.

    Конструктор класса: отсутствует.

    Список доступных атрибутов класса:
    | TAB_SPACE_6
    | TAB_SPACE_9
    | TAB_SPACE_11
    | PEER_ID_ADDITION_INT
    | RANDINT_BOTTOM_BOUND
    | RANDINT_TOP_BOUND
    | END_OF_LOGS_LINE
    | TIME_DELAY_1
    | TIME_DELAY_5
    | TIME_DELAY_10
    | QUIZ_TIME_DELAY_SAMPLE
    | MEMBER_QUANT_TO_KEEP_BLITZ
    | мMEMBERS_FINISH_BOUND
    """
    TAB_SPACE_6 = '\t' * 6
    TAB_SPACE_9 = '\t' * 9
    TAB_SPACE_11 = '\t' * 11
    PEER_ID_ADDITION_INT = 2000000000
    RANDINT_BOTTOM_BOUND, RANDINT_TOP_BOUND = -30000000, 30000000
    END_OF_LOGS_LINE = f"{'=' * 30}[Конец логирования]{'=' * 30}"
    TIME_DELAY_1, TIME_DELAY_5, TIME_DELAY_10 = 1, 5, 10
    QUIZ_TIME_DELAY_SAMPLE = 60
    MEMBER_QUANT_TO_KEEP_BLITZ = 2
    MEMBERS_TO_FINISH_BOUND = 1
