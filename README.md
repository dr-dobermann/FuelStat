# FuelStat
A program that expands fuel statistics

![GitHub Logo](/images/logo.png)


**Задача из книги Чарльза Уэзерелла "Этюды для программистов".**

**Горючие слезы, или Учет расхода бензина**
Задача состоит в том, чтобы привести статистику,
исходя из созданной пользователем таблицы.

# Основные условия:
Известно, что каждой новой записи в журнале соответсвует
новая **полная заправка**. Исходя из этого можно сказать,
что количество галлонов, которые он покупает на новой заправке
показывают, сколько галлонов он потратил после прошлой заправки
Следовательно в строке с новой заправкой
указывается расстояние пройденное до новой заправки и 
количество галлонов, которые были потрачены после
предыдущей заправки. А цена голона и цена купленных голонов с
новой заправки. 


# Исльзование:
Для того, чтобы запустить программу нужно:
1. Создать или изменить файлы в которых содержаться данные о запрвках
    и транзакциях. Инструкция по заполнению этих файлов находится ниже.
    Находяться они в папке data.
    fuel.csv - данные о заправках
    trans.csv - данные о транзакциях(покупке топлива)
2. Запустить программу: python3 main.py
3. ...

# Заполнение файлов с данными:
- Данные записываеются через запятую
- Новый зарпавка -- новая строчка.
## Файл с данными о заправке:
1. Название заправки.
2. Цена за один галлон.
Пример:
Texaco, 59.9
## Файл с данными о транзакциях:
1. Дата.
2. Пробег.
3. Номер марки бензина из файла заправок.
4. Количество галлонов


## Как это работает:
1. Пользователь создает тесктовый файл, в котором указывает
    данные о заправке(Название, цена за галлон).
2. Затем создает еще один текстовый файл, в котором указывает
    данные о транзакциях(номер заправки(порядковый номер заправки
    из предыдущего файла), пробег на автомобиле, количество галлонов).
3. Получаем созданные пользователем файлы и начинаем работать с ними.
4. Создаем базу данных.
5. Создаем таблицы в базе данных.
6. Вставляем данные из фалов в таблицы.
6. Обединяем созданные таблицы в одну.
7. Находим расстояние, которое мы проехали между двумя разными
    заправками:
    1. Если это первая заправка:
        1. Cохраняем ее название и номер строки.
        1. Переходим к следующей строке.
    2. Если названия заправок одинаковые:
        1. Если эта заправка последняя:
            1. Переходим к пп. 4.
        2. Иначе:
            1. Переходим к следующей строке(заправке).
    3. Если названия заправок разные:
        1. Сохраняем название и номер строки.
        2. Отнимаем расстояние старой заправки от
            расстояния заправки с новым названием.
        3. Выводим полученной значение в таблицу.
        4. Вместо названия и номера сроки старой заправки,
            устанавливаем название и номер строки текущей заправки
        5. Если это последняя заправка:
            1. Переходим к пп. 4.
        6. Иначе:
            1. Переходим к следующей строке.
            2. Переходим к пп. 3.2.
8. Находим пройденное расстояние на одном галлоне:
    1. Если это первая заправка:
        1. Переходим к следующей.
    2. Находим расстояние, которое автомобиль прошел после предыдущей
        заправки
        1. Отнимаем расстояние до предыдущей заправки от
            расстояния до текущей заправки.
        2. Полученной расстояние делим на количесво галлонов купленных
            на текущей заправке.
        3. Выводим полученное значение в таблицу.
        4. Если это последняя заправка:
            1. Переходим к пп. 5.
        5. Иначе:
            1. Переходим к следующей строке
            2. Переходим к пп. 4.2.
9. Находим стоимость одной мили:
    1. Если это первая заправка:
        1. Переходим к следующей строке.
    2. Находим количество галлонов потраченных за одну милю
        1. Отнимаем расстояние до предыдущей заправки от
            расстояния до текущей заправки.
        2. Количество галлонов, которые мы заправили на текущей
            заправки делим на полученное расстояние.
        3. Полученное значение умножаем на цену галлона предыдущей
            заправки.
        4. Выводим полученное значение в таблицу.
        5. Если это последняя заправка:
            1. Переходим к пп. 6. 
        4. Иначе:
            1. Переходим к следующей строке
            2. Переходим к пп. 5.2.
10. Находим стоимость одного дня:
    1. Создадим цену дня равную нулю.
    2. Если это первая заправка:
        1. Сохраняем дату.
        2. Прибавляем к цене дня сумму.
        3. Переходим к следующей строке.
    3. Проверяем дату заправки.
        1. Если даты совпадают:
            1. Прибавляем к цене дня сумму.
            2. Если это последняя заправка:
                1. Выводим цену дня в таблицу
            3. Иначе:
                1. Переходим к следующей заправке
        2. Если даты не совпадают:
            1. Выводим сумму дня в таблицу.
            2. Если это не последняя заправка:
                1. Сохраняем дату.
                2. Обнуляем цену дня.
                3. Прибавляем к цене дня сумму.
                4. Переходим к следующему заправке.
                2. Переходим к пп 6.3.