import requests
import json
import webbrowser
from enum import Enum

# При значении True программа будет логировать свои действия, также она сохранит резульат действия в файл.
LOG = False

class Errors(Enum):
    WEB = "Невозможно открыть ссылку"
    REQUEST = "Ошибка запроса"
    USER_INPUT = "Ошибка ввода пользователя"
    FORMAT = "Некорректный формат данных"
    VALUE_INVALID = "Неверное значение"

class WikiPaser:
    def wiki_search(self, name: str):
        """
        Выполняет поиск на википедии по определенному запросу пользователя
        :param name:
        :return: Список вариантов поиска.
        """
        # Параметры запроса
        params = {"action": "query",
                  "list": "search",
                  "utf8": "",
                  "format": "json",
                  "srsearch": name.strip()}
        # Получаем ответ
        try:
            request = requests.get("https://ru.wikipedia.org/w/api.php?", params=params)
        except requests.RequestException as ex:
            UserWork.print_error(Errors.REQUEST)
            print(ex)
            return 1

        if LOG:
            print(request.url)  # LOGGING!

        # Parse and save as file
        parsed = request.json()
        if LOG:
            with open("result.json", 'w') as f:
                json.dump(parsed, f, indent=2)

        parsed = parsed["query"]
        return parsed["searchinfo"]["totalhits"], parsed["search"]


    def open_page(self, pageid):
        url = f"https://ru.wikipedia.org/w/index.php?curid={pageid}"
        try:
            webbrowser.open(url)
        except:
            UserWork.print_error(Errors.WEB)

    def print_list(self, result):

        i = 1
        for page in result:
            print(f"{i}. {page['title']}")
            i += 1


class UserWork:
    def __init__(self):
        pass

    def read_request(self):
        # Считывание запроса пользователя.
        user_input = input("Введите ваш запрос: ").strip()

        if len(user_input) == 0:
            UserWork.print_error(Errors.USER_INPUT)
            return 1

        return user_input


    @staticmethod
    def print_error(typo : Errors):
        print(f"[ERROR]: {typo.value}")



# Основной метод программы
def main():

    # Считывание запроса от пользователя
    workspace = UserWork()
    user_input = workspace.read_request()

    # Проверка запроса на ошибки
    if user_input == 1:
        return

    # Создание экземпляра класса для работы с википедией
    wiki = WikiPaser()
    n, result = wiki.wiki_search(user_input)


    if n == 0:
        print("По вашему запросу не найдено результатов.")
    else:
        print(f"По вашему запросу найдено {n} результатов.")
        # Вывод списка резульатов
        wiki.print_list(result)

        # Ввод номера страницы пользователя

        user_number = input("Введите номер страницы: ")
        try:
            user_number = int(user_number)
        except:
            UserWork.print_error(Errors.FORMAT)
            return


        if 0 < user_number <= 10 and user_number <= n:
            wiki.open_page(result[user_number - 1]["pageid"])
        else:
            UserWork.print_error(Errors.VALUE_INVALID)




if (__name__ == "__main__"):
    main()
