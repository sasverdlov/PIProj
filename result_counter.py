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
    def map_uid_login(user_fio_or_email):
        sqlite_select_query = f"""SELECT DISTINCT id from user WHERE username IN ('{user_fio_or_email.lower()}') OR email IN ('{user_fio_or_email.lower()}')"""
        cursor.execute(sqlite_select_query)
        id = cursor.fetchall()
        if id:
            return id[0][0]
    try:
        sqlite_connection = sqlite3.connect("app.db")
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")
        user_id = map_uid_login(str(user_id))
        sqlite_select_query = f"""SELECT DISTINCT q_id, answ from results WHERE u_id == {user_id} AND q_id IN ({','.join(map(str, questions_ids))}) ORDER BY timestamp ASC"""
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
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
        self.results_raw = read_methodic_answer_rows(self.user_id.lower(), self.questions)
        self.enough_results = True if self.results_raw and len(self.results_raw) == len(self.questions) else False
        self.results_counted = self.count_f(self.results_raw) if self.enough_results else None
        self.max_scale_x = methodic.max_scale_x


def count_scale_mono(results: dict, mapping: dict):
    def count_all(questions: list):
        return sum({k: mapping[v] for k, v in results.items() if k in questions}.values())

    return count_all


def count_scale_binary(results: dict, mapping: dict):
    mappingT, mappingF = mapping, {k: abs(v - 1) for k, v in mapping.items()}

    def count_subscales(questions_t: list, questions_f: list):
        t = count_scale_mono(results, mappingF)(questions_f)
        f = count_scale_mono(results, mappingT)(questions_t)
        return t + f

    return count_subscales


def count_scale(results: dict, mapping: dict):
    csm = count_scale_mono(results, mapping)
    csb = count_scale_binary(results, mapping)

    def selector(*args):
        if len(args) == 1:
            return csm(*args)
        elif len(args) == 2:
            return csb(*args)
        else:
            raise Exception("More than 2 lists passed!")

    return selector


def count_diner(raw_data: dict) -> dict:
    mapping = {"Верно": 1, "Неверно": 0}
    cs = count_scale(raw_data, mapping)
    Lsum = cs([5, 11, 24, 47, 58])
    Fsum = cs([22, 24, 61], [9, 12, 15, 19, 30, 38, 48, 49, 58, 59, 64, 71])
    Ksum = cs([11, 23, 31, 33, 34, 36, 40, 41, 43, 51, 56, 61, 65, 67, 69, 70])
    Hssum = cs([1, 2, 6, 37, 45], [9, 18, 26, 32, 44, 46, 55, 62, 63])
    Dsum = cs([1, 3, 6, 11, 28, 37, 40, 42, 60, 65, 61], [9, 13, 11, 18, 22, 25, 36, 44])
    Hysum = cs([1, 2, 3, 11, 23, 28, 29, 31, 33, 35, 37, 40, 41, 43, 45, 50, 56], [9, 13, 18, 26, 44, 46, 55, 57, 62])
    Pdsum = cs([3, 28, 34, 35, 41, 43, 50, 65], [7, 10, 13, 14, 15, 16, 22, 27, 52, 58, 71])
    Pasum = cs([28, 29, 31, 67], [5, 8, 10, 15, 30, 39, 63, 64, 66, 68])
    Ptsum = cs([2, 3, 42], [5, 8, 13, 17, 22, 25, 27, 36, 44, 51, 57, 66, 68])
    Sesum = cs([3, 42], [5, 7, 8, 10, 13, 14, 15, 16, 17, 26, 30, 38, 39, 46, 57, 63, 64, 66])
    Masum = cs([43], [4, 7, 8, 21, 29, 34, 38, 39, 54, 57, 60])

    res = {'L': Lsum, 'F': Fsum, 'K': Ksum, 'Hs': Hssum + (Ksum * 0.51), 'D': Dsum, 'Hy': Hysum,
           'Pd': Pdsum + (Ksum * 0.4), 'Ра': Pasum, 'Pt': Ptsum + Ksum, 'Se': Sesum + Ksum, 'Ma': Masum + (Ksum * 0.2)}

    def prettify_result(i):
        return int(i) if int(i) - i == 0 else round(i, 2)

    return {k: prettify_result(v) for k, v in res.items()}


def get_methodic(methodic_id):
    if methodic_id == 1:
        return Methodic(1, "Сокращенный многофакторный опросник для исследования личности", range(1, 72), count_diner,
                        20)
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
