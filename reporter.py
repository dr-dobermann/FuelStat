import logging
import database
# from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Flowable
from reportlab.lib.styles import getSampleStyleSheet


# TODO: Сделать список стилей
# TODO: Вывести подробную статистике
# TODO: Описать функции создания статистик
# TODO: Починить информацию о параметрах(ошибка при отсутствии дат)




class MyLine(Flowable):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
    
    def draw(self):
        self.canv.line(0, self.height, self.width, self.height)



class Reporter():
    """
    Класс создания отчета
    """

    def __init__(self, start_date=None, end_date=None, gas_names=None,
                 file_name=None):
        """
        Инициализация класса.
        Создаем документ, который затем будет содержать
        и выводить свои элементы.

        Parameters
        ----------
        start_data : str
            Дата, с которой будет начинаться отчет.
        end_data : str
            Конечная дата отчета.
        gas_name : str
            Названия заправок по которым будет строиться отчет.
        file_name : str
            Название файла отчета.
        """

        self.start_date = start_date
        self.end_date = end_date
        self.gas_names = gas_names
        self.file_name = file_name

        self.logger = logging.getLogger("REPORTER")  
        self.logger.debug("Report parameters: start_date[" + str(self.start_date) + ']' +
                          ", end_date[" + str(self.end_date) + ']' +
                          ", gas_names[" + str(self.gas_names) + ']' +
                          ", file_name[" + str(self.file_name) + ']')
    
        self.db = database.DataBase("data/database.db")
    
        # Создаем строку условия для получения данных из базы данных
        self.logger.debug("Creating main condition to select data from data base")
        self.condition = ""
        if self.start_date is not None:
            condition = self.upd_condition(self.condition, "dtime >= '" + str(self.start_date) + "'")
        if self.end_date is not None:
            self.condition = self.upd_condition(self.condition, "dtime <= '" + str(self.end_date) + "'")
        if self.gas_names is not None:
            self.condition = self.upd_condition(self.condition, "name in " + str(tuple(self.gas_names)))
        self.logger.debug("Conditions is + " + condition)
        self.logger.info("Condition was created")

        # Cоздаем документ, в котором будут содержать полученные данные
        self.logger.debug("Creating DocTemplate")
        self.doc = SimpleDocTemplate("data/" + file_name + ".pdf",
                                     pagesize=A4,
                                     topMargin=5 * mm,
                                     bottomMargin=5 * mm,
                                     leftMargin=10 * mm,
                                     rightMargin=10 * mm,
                                     showBoundary=0)
        self.logger.info("DocTemplate was created")

        self.elements = [] # Список, который будет содержать все элементы документа


        # Создаем нужные нам стили
        styles = getSampleStyleSheet()
        self.s_header_1 = styles["Heading1"]
        self.s_header_1.alignment = TA_CENTER
        self.s_param = styles["Normal"]
        self.s_param.fontSize = 12
        self.s_param.spaceAfter = 10
        self.s_header_2 = styles["Heading2"]
        self.s_header_2.alignment = TA_CENTER
        self.s_table = [("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ('ALIGN', (0, 0), (-1, -1), "CENTER"),
                        ('VALIGN', (0, 0), (-1, -1), "MIDDLE")]


        # Название документа
        self.elements.append(Paragraph("FuelStatReport", self.s_header_1))
        self.elements.append(Spacer(0, 20))

        # Информация о параметрах отчета
        param_info = "Start Date: " + self.start_date 
        param_info += "&nbsp;&nbsp;&nbsp;&nbsp; End Date: " + self.end_date
        gs = ""
        # Создаем строку с названями заправки
        if self.gas_names is None:
            gs = "All"
        else:
            gs = str(self.gas_names[0])
            for n in self.gas_names:
                gs += ", " + str(n)
        param_info += "&nbsp;&nbsp;&nbsp;&nbsp; Gas Stations: " + gs
        self.elements.append(Paragraph(param_info, self.s_param))

        # Рисуем линию после параметров отчета
        self.elements.append(MyLine(self.doc.width, 0))
        self.elements.append(Spacer(0, 20))



    
    def create_report(self, main_info=True, short_stat=True, full_stat=True):
        if main_info is True:
            self.elements.extend(self.gen_main_info())
        if short_stat is True:
            self.elements.extend(self.gen_short_stat())
        if full_stat is True:
            self.elements.extend(self.gen_full_stat())
        self.doc.build(self.elements)


    def gen_main_info(self):
        """
        Генерирует элементы для основоного отчета,
        в котором будет данные о заправках. \n
        Не формирует статистистическую информацию! \n
        Данные:
        - Дата заправки;
        - Название заправки;
        - Расстояние пройденное до этой заправки(мили);
        - Цена одного галлона(центы);
        - Расстояние, пройденное после предыдущей заправки(мили);
        - Количество галлонов;
        - Общая стоимость заправки(доллары);
        - Расстояние пройденно на одном галлоне(мили);
        - Цена одной мили(доллары);
        - Цена одного дня(доллары);

        Returns
        -------
        list:
            Список элементов основного отчета
        """

        elements = []

        # Получаем данные из базы данных
        # Условия получения информации из вьюшки для цены дня:
        # Если дата текущей заправки равна дате предыдущей заправки,
        # то прибавляем ее цену к сумме.
        # Если даты разные, то сохраняем сумму в предыдущую заправку, затем
        # сумму приравниваем к цене текущей запраки.
        table_data = self.table_data_to_list(
            self.db.select("v_trans vv", 
                           """dtime,
                           name,
                           odometer,
                           mbs,
                           price,
                           amount,
                           cost,
                           mpg,
                           mile_price,
                           CASE next_dtime = dtime
                              WHEN FALSE
                                THEN (
                                      SELECT SUM(v.cost) 
                                      FROM v_trans v 
                                      WHERE v.dtime = vv.dtime
                                      GROUP BY v.dtime
                                     )
                           END
                            """,
                           self.condition + " ORDER BY dtime"))

        table_data.insert(0,
                          ["DATE", "GAS", "ODOMETER",
                           "MILIAGE \n BEETWEEN",
                           "GALLON \n PRICE",
                           "GALLONS", "COST", "MPG", 
                           "MILE \n PRICE", "DAY \n PRICE"])


        # После получения данных из вьюшки нужно создать список,
        # в котором будут хранится строки,
        # которые нужно объединить объединить в таблице.
        # Элемент списка будет выглядить вот так: [s_cell, e_cell]
        merge_rows = []
        merging = False
        # В списке, который мы получили от базы данны, проверяем:
        self.logger.debug("Creating merging rows list for document's table")
        for i in range(1, len(table_data)):
            # Если ячейка цены дня пустая и флажок объединения не активен:
            if table_data[i][9] is None and merging is False:
                # Записываем текущую строку, как начальную для объединения и
                # активируем флажок объединения.
                merge_rows.append([i, ])
                merging = True
            # Если ячейка цены дня не пустая и флажок объединения активен,
            elif table_data[i][9] is not None and merging is True:
                # то указываем текущую ячейку, как конечную для объединения и
                # выключаем флажок объединения.
                table_data[merge_rows[len(merge_rows) - 1][0]][9] = table_data[i][9]
                merge_rows[len(merge_rows) - 1].append(i)
                merging = False
        self.logger.debug("Merging rows is " + str(merge_rows))
        self.logger.info("Merging rows list was created")


        # Создаем таблицу
        self.logger.debug("Creating document's main table")
        table = Table(table_data, repeatRows=True)
        table_style = self.s_table
        for row in merge_rows:
            table_style.append(("SPAN", (9, row[0]), (9, row[1])))
        table.setStyle(TableStyle(table_style))
        self.logger.info("Document's main table was created")
        elements.append(table)
        elements.append(Spacer(0, 30))

        return elements



    def gen_short_stat(self):
        """
        Генерирует элементы для краткой статистике в отчете. \n
        Генерирует таблицу, которую заполняет данными. \n
        Данные:
        - Общее пройденное расстояние(мили).
        - Среднее расстояние между заправками(мили).
        - Средняя цена галлона(центы).
        - Среднее количество галлонов.
        - Средняя цена одной заправки(доллары).
        - Средний пробег на одном галлоне(мили).
        - Средняя цена одной мили(доллары).
        - Средняя цена одного дня(доллары).
        - Общая стомость заправок(доллары).
        - Средний расход топлива(галлоны).

        Returns
        -------
        list
            Элементы краткой статистики
        """

        elements = []

        # Данные по статистике
        elements.append(Paragraph("Short Statistics", self.s_header_2))
        elements.append(Spacer(0, 10))

        table_data = self.table_data_to_list(
            self.db.select("v_trans",
                           """
                           MAX(odometer) - MIN(odometer),
                           AVG(mbs),
                           AVG(price),
                           AVG(amount),
                           AVG(cost),
                           AVG(mpg),
                           AVG(mile_price),
                           cost
                           """,
                           self.condition))

        table_data.insert(0, 
                          ["TOTAL \n DISTANCE",
                           "AVERAGE \n MILIAGE \n BEETWEEN",
                           "AVERAGE \n GALLON \n PRICE",
                           "AVERAGE \n GALLONS",
                           "AVERAGE \n COST", "AVERAGE \n MPG",
                           "AVERAGE \n MILE \n PRICE",
                           "AVERAGE \n DAY PRICE"])
        # Создаем таблицу
        self.logger.debug("Creating document's stat table")
        table = Table(table_data, repeatRows=True)
        table_style = self.s_table
        table.setStyle(TableStyle(table_style))
        self.logger.info("Document's stat table was created")

        elements.append(table)
        elements.append(Spacer(0, 20))
        # (SELECT name FROM v_trans WHERE price = (SELECT MAX(price) FROM v_trans))

        return elements

    

    def gen_full_stat(self):
        return []


    def table_data_to_list(self, data):
        c = []
        for row in data:
            lst = []
            for e in row:
                if type(e) is float:
                    e = round(e, 2)
                lst.append(e)
            c.append(lst)
        return c


    def upd_condition(self, source, addition):    
        if source == "":
            source = addition
        else:
            source += " AND " + addition
        return source