import ast
import sqlite3
import io

from matplotlib.figure import Figure
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from app import db


def get_all_methodics():
    pass


def read_methodic_answer_rows(user_id: int, questions_ids: list):
    try:
        sqlite_connection = sqlite3.connect("app.db")
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")
        sqlite_select_query = f"""SELECT DISTINCT q_id, answ from results WHERE u_id == {user_id} AND q_id IN ({','.join(map(str, questions_ids))}) ORDER BY timestamp ASC"""
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        cursor.execute(sqlite_select_query)
        return {k: v for k, v in cursor.fetchall()}
        # print("Чтение ", row_size, " строк")
        # records = cursor.fetchmany(row_size)
        # print("Вывод каждой строки \n")
        # for row in records:
        #     print("ID:", row[0])
        #     print("Имя:", row[1])
        #     print("Почта:", row[2])
        #     print("Добавлен:", row[3])
        #     print("Зарплата:", row[4], end="\n\n")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


class Methodic:
    def __init__(self, i: int, name: str, questions: range, count_f, max_scale_x: int):
        self.i = i
        self.name = name
        self.questions = list(questions)
        self.results_raw = None
        self.results_counted = None
        self.count_f = count_f
        self.start_point = self.questions[0]
        self.max_scale_x = max_scale_x

    def __str__(self):
        r = f"Methodic №{self.i}, named {self.name}, questions: {self.questions}"
        if self.results_raw:
            r += f"\n raw results: {self.results_raw}"
        if self.results_counted:
            r += f"\n final results: {self.results_counted}"
        return r


class UserResult(Methodic):
    def __init__(self, methodic, user_id):
        super().__init__(methodic.i, methodic.name, methodic.questions, methodic.count_f, methodic.max_scale_x)
        self.user_id = user_id
        self.results_raw = read_methodic_answer_rows(self.user_id, self.questions)
        self.enough_results = True if self.results_raw and len(self.results_raw) == len(self.questions) else False
        self.results_counted = self.count_f(self.results_raw) if self.enough_results else None
        self.max_scale_x = methodic.max_scale_x


def count_diner(raw_data: dict) -> dict:
    mappingT = {"Верно": 1, "Неверно": 0}
    mappingF = {"Верно": 0, "Неверно": 1}
    Lsum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (5, 11, 24, 47, 58)}.values())
    Fsum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (22, 24, 61)}.values()) + sum(
               {k: mappingT[v] for k, v in raw_data.items() if
                k in (9, 12, 15, 19, 30, 38, 48, 49, 58, 59, 64, 71)}.values())
    Ksum = sum({k: mappingF[v] for k, v in raw_data.items() if
                k in (11, 23, 31, 33, 34, 36, 40, 41, 43, 51, 56, 61, 65, 67, 69, 70)}.values())
    Hssum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (1, 2, 6, 37, 45)}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if k in (9, 18, 26, 32, 44, 46, 55, 62, 63)}.values())
    Dsum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (1, 3, 6, 11, 28, 37, 40, 42, 60, 65, 61)}.values()) + sum(
               {k: mappingT[v] for k, v in raw_data.items() if k in (9, 13, 11, 18, 22, 25, 36, 44)}.values())
    Hysum = sum({k: mappingF[v] for k, v in raw_data.items() if
                 k in (1, 2, 3, 11, 23, 28, 29, 31, 33, 35, 37, 40, 41, 43, 45, 50, 56)}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if k in (9, 13, 18, 26, 44, 46, 55, 57, 62)}.values())
    Pdsum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (3, 28, 34, 35, 41, 43, 50, 65)}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if
                 k in (7, 10, 13, 14, 15, 16, 22, 27, 52, 58, 71)}.values())
    Раsum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (28, 29, 31, 67)}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if k in (5, 8, 10, 15, 30, 39, 63, 64, 66, 68)}.values())
    Ptsum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (2, 3, 42)}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if
                 k in (5, 8, 13, 17, 22, 25, 27, 36, 44, 51, 57, 66, 68)}.values())
    Sesum = sum({k: mappingF[v] for k, v in raw_data.items() if k in (3, 42)}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if
                 k in (5, 7, 8, 10, 13, 14, 15, 16, 17, 26, 30, 38, 39, 46, 57, 63, 64, 66)}.values())
    Masum = sum({k: mappingF[v] for k, v in raw_data.items() if k == 43}.values()) + sum(
                {k: mappingT[v] for k, v in raw_data.items() if
                 k in (4, 7, 8, 21, 29, 34, 38, 39, 54, 57, 60)}.values())

    res = {'L': Lsum, 'F': Fsum, 'K': Ksum, 'Hs': Hssum+(Ksum*0.51), 'D': Dsum, 'Hy': Hysum, 'Pd': Pdsum+(Ksum*0.4), 'Ра': Раsum, 'Pt': Ptsum+Ksum, 'Se': Sesum+Ksum, 'Ma': Masum+(Ksum*0.2)}
    return res


def get_methodic(methodic_id):
    if methodic_id == 1:
        return Methodic(1, "Сокращенный многофакторный опросник для исследования личности", range(1, 72), count_diner, 20)
    else:
        raise Exception("Methodic is not present")


def get_user_results(methodic, user_id):
    res = UserResult(methodic, user_id)
    return res


# def make


def create_figure(data):
    max_scale_x, data = data.split("scale")
    data = ast.literal_eval(data)
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(range(len(data)), list(data.values()), align='center')
    # axis.bar(*zip(*data.items()))
    return fig


def diagram(data):
    fig = create_figure(data)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')
