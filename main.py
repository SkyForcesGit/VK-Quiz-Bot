# Script name: main.py
# Author(s): SkyForces
# Modification date: January 2023
# License: MIT License, read 'LICENSE.txt'
# Copyright (c) 2023, SkyForces and Contributors

"""
Данный скрипт отвечает за инициализацию и запуск бота, а также за завершение его работы.
Опирается на использование пакета "vkquizbot".
"""

# Стандартная библиотека
import threading
import traceback

# Модули бота
from vkquizbot import bot_core, utils


# pylint: disable=broad-except
if __name__ == "__main__":
    try:
        bot = bot_core.BotCore()
        console_thread = threading.Thread(target=bot.console.console_mainloop(), daemon=False,
                                          name="ConsoleThread")
        console_thread.start()

        while console_thread.is_alive():
            continue
    except BaseException as exc:
        utils.ErrorNotifier.create_exception_flag(exc.__class__.__name__, traceback.format_exc())
    finally:
        del bot
