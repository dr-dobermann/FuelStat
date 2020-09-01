# from reportlab.pdfgen import canvas
import logging

import database


# TODO: Дополнить документацию
# TODO: Добавить таблцу заправок
# TODO: Добавить таблицу транзакций
# TODO: Добавить параметры при запуске
# TODO: Добавить функцию считывания данных из файлов для создания базы данных
# TODO: Добавить логгирование



def main():
    # Инициализируем logging
    logging.basicConfig(filename="logging.log", level=logging.DEBUG, format="%(asctime)s %(name)s [%(levelname)s] : %(message)s")
    logger = logging.getLogger("MAIN")

    # Создаем базу данных заправок
    fuel = database.DataBase("fuel")

    fuel.create_table('''id INTEGER PRIMARY KEY,
                         name TEXT NOT NULL,
                         price REAL NOT NULL''')

    f = open("data/fuel.txt")
    data = []
    for line in f:
        data.append(tuple(line.split(",")))
    
    print(data)

    fuel.insert_list("name, price", data)

    # for row in fuel.select():
    #     print(row)
    print(fuel.select())


    # # Создаем pdf файл с таблицой
    # pdf_tabel = canvas.Canvas("fuel.pdf")
    # pdf_tabel.drawString(0, 0, str(dbc.fetchone()))
    # pdf_tabel.save()



if __name__ == "__main__":
    main()