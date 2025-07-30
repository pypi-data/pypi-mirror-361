import os
import importlib
import platform
import socket
import psutil
import sys
import time

def help(choice="en"):
    choice = choice.lower()
    if choice == "en":
        print("OK, please visit our website - https://pypi.org/project/xa-izipy/")
    elif choice == "ru":
        print("Привет, благодарю вас за использование моей библиотеки! Данная библиотека может помочь использовать Python проще!\n"
              " В данной библиотеке есть 2 функции:\n\n"
              "  - help() - Ну, вы сейчас и используете данную команду)\n"
              "  - getdirectory() - Позволяет легко и без боли узнать в какой папке выполняется код\n"
              "  - fast_import() - Помогает быстро загрузить основные библиотеки(os, time, random, logging, json)\n"
              "  - get_platform_info() - Помогает узнать инфомарцию про устройство(система, версия, архитектура, имя устройства в сети, сколько ОЗУ, сколько доступно ОЗУ)\n",
              "  - typing_text() - поможет выводить текст с анимацией тайпинга(текст, задерка)\n",
              "\nВся информация находится на нашем сайте - https://pypi.org/project/xa-izipy/")
    else:
        print("Please choose the correct language RU/EN")

def getdirectory():
    return os.path.dirname(os.path.abspath(__file__))

def fast_import(show_loading=True):
    list_libs = [
        "os",
        "time",
        "random",
        "logging",
        "json"
    ]

    for lib in list_libs:
        try:
            importlib.import_module(lib)
            if show_loading == True: print(f"Success load lib: {lib}")
        except Exception as e:
            print(f"Error loading this default lib: {lib}\nError: {e}")
    if show_loading == True: print()

def get_platform_info():
    ram = psutil.virtual_memory()
    return {
        "os": platform.system(),
        "release": platform.release(),
        "arch": platform.machine(),
        "hostname": socket.gethostname(),
        "ram_total_GB": round(ram.total / (1024 ** 3), 2),
        "ram_available_GB": round(ram.available / (1024 ** 3), 2)
    }

def typing_text(text="", speed=0.3):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)