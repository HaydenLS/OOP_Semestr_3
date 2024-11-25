import os.path
import xml.etree.ElementTree as ET
import time

# Тестовый путь до файла
TEST_PATH = "test.xml"


class File:
    def __init__(self, path=TEST_PATH):
        self.path = path

    def read_line(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            for line in file:
                yield line.strip()

    def getline(self, line):
        return line

    def read_file(self):
        # Хеш таблица для всех элементов
        hash_table = dict()
        # Словарь дубликатов, где ключ - hash_code(elem), значение - количество дубликатов
        double_dict = dict()

        start1 = time.time()
        for line in self.read_line():
            # Получаем кортеж значений
            text = self.get_line(line)
            if text != None:
                # Получаем полный хеш-код нашего элемента
                hash_code = hash(text)

                # Проверяем на дубликат. Если находим, добавляем в словарь дубликатов,
                # Если нет - сохраняем в хеш таблицу
                if hash_code in hash_table:
                    double_dict[hash_code] = double_dict.get(hash_code, 0) + 1
                else:
                    hash_table[hash(text)] = text
        end1 = time.time()

        # Вывод дублирующихся записей
        print("Дубликаты:")
        for i in double_dict:
            print(f"Запись: {hash_table[i]}, Количество повторений: {double_dict[i]}")

        # Вывод времени, которое потратили для посика дубликатов.
        print(f"Время, затраченное на сохранение адресов и посик дубликатов: {end1 - start1}")

        # Подсчет сколько в каждом городе: 1, 2, 3, 4 и 5 этажных зданий.
        start2 = time.time()
        new_hash = dict()
        for value in hash_table.values():
            # Превращаем элемент обратно в словарь и получаем данные
            v_dict = dict(value)
            # print(f"Достали элемент: {v_dict}")
            city_name_hash = hash(v_dict['city'])
            element = list
            if city_name_hash in new_hash:
                # Извлекаем элемент
                element = list(new_hash[city_name_hash])
            else:
                element = [v_dict['city'], (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
            floor = int(v_dict['floor'])
            element[floor] = (floor, element[floor][1] + 1)

            new_hash[city_name_hash] = tuple(element)
        end2 = time.time()

        # Вывод итогового резульата по количеству домов
        print("Итог: ")
        for elem in new_hash.values():
            print(f"В городе {elem[0]} зданий с количеством этажей: ")
            for i in range(1, 6):
                print(f"{i}-этажки - {elem[i][1]} штук")

        # Вывод времени, которое потратили для нахождения домов.
        print(f"Время, затраченное на отображение количества 1-5 этажных зданий в каждом городе. {end2 - start2}")
        # Итоговое время
        print(f"Итоговое время работы программы: {end2 - start1}")


class XmlFile(File):
    def __init__(self, path):
        super().__init__(path)

    def get_line(self, line: str):
        """
        Парсинг строки xml превращая ее в вид (('key1', 'value1'),'key2', 'value2', ...)
        :param line: Строка вида <item key1=value1 key2=value2 ... />
        :return: Кортеж вида (('key1', 'value1'),'key2', 'value2', ...)
        """
        if line.startswith("<") and line.endswith('/>'):
            # Парсим строку как XML
            element = ET.fromstring(line)
            # Получаем атрибуты
            attributes = list(element.attrib.items())
            # Возвращаем в виде кортежа
            return tuple(attributes)


class CsvFile(File):
    def __init__(self, path):
        super().__init__(path)

    def get_line(self, line):
        """
        Парсинг строки csv превращая ее в вид (('key1', 'value1'),'key2', 'value2', ...)
        :param line: Строка вида value1;value2; ... />
        :return: Кортеж вида (('key1', 'value1'),'key2', 'value2', ...)
        """
        template = ["city", "street", "house", "floor"]
        line = [i.strip("\"") for i in line.split(';')]

        if line != template:
            result = tuple(zip(template, line))
            return result


class UserWork:
    path_xml = "Files/address.xml"
    path_csv = "Files/address.csv"

    def start_cycle(self):
        print("Вам необходимо ввести путь до файла справочника. Если вы не хотите вводить путь, то введите:\n"
              f"1 - {self.path_xml}\n"
              f"2 - {self.path_csv}\n"
              "0 - Завершение программы"
              )
        user_path = input("Введите путь/значение: ")
        if user_path == '1':
            file = XmlFile(self.path_xml)
        elif user_path == '2':
            file = CsvFile(self.path_csv)
        elif user_path == '0':
            return 0
        else:
            if not os.path.exists(user_path):
                print("[ERROR] Путь не найден, попробуйте еще раз.")
                return 1

            _, type = user_path.split('.')
            if type == 'xml':
                file = XmlFile(self.path_xml)
            elif type == 'csv':
                file = CsvFile(self.path_csv)
            else:
                print("[ERROR] Неизвестный тип файла. Нужен xml или csv")
                return 1

        file.read_file()

    def start_program(self):
        while True:
            print("")
            result = self.start_cycle()
            if result == 0:
                break


if __name__ == "__main__":
    print("Начало программы. Не забудьте создать папку Files с файлами address.csv и address.xml")
    program = UserWork()
    program.start_program()
