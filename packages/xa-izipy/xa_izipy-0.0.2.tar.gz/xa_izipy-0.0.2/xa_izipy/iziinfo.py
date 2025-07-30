import os

def help():
    choice = input("Choose your language:\n - EN\n - RU\n\nChoice: ").lower()
    if choice == "en":
        print("OK, please visit our website - https://pypi.org/project/xa-izipy/")
    elif choice == "ru":
        print("Привет, благодарю вас за использование моей библиотеки! Данная библиотека может помочь использовать Python проще!\n"
              " В данной библиотеке есть 2 функции:\n\n"
              "  - help() - Ну, вы сейчас и используете данную команду)\n"
              "  - getdirectory() - Позволяет легко и без боли узнать в какой папке выполняется код")
    else:
        print("Please choose the correct language")

def getdirectory():
    return os.path.dirname(os.path.abspath(__file__))

