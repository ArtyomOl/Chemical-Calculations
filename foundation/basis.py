import json

from maths.functions import Func
import maths
from storage.db import create_connection
from config.config import user_name


connection = create_connection()


class Experiment:
    def __init__(self, first_element: str, second_element: str, temperature, pressure, source_data: dict, article: int):
        self.first_element = first_element
        self.second_element = second_element
        if pressure == None:
            pressure = 'NULL'
        if temperature == None:
            temperature = 'NULL'
        self.temperature = temperature
        self.pressure = pressure
        self.source_data = source_data
        self.article = article

    # добавление эксперимента в бд
    def addIntoDB(self):
        cursor = connection.cursor()
        source_data_json = json.dumps(self.source_data)
        insert_query = f"INSERT INTO experiments (first_element, second_element, temperature, pressure, source_data, article) VALUES " \
                       f"('{self.first_element}', '{self.second_element}', {str(self.temperature)}, {str(self.pressure)}, '{source_data_json}', '{str(self.article)}');"
        cursor.execute(insert_query)
        connection.commit()


class Element:
    def __init__(self, name: str, specifications_string: str):
        self.name = name
        self.specifications_string = specifications_string

    # добавление элемента в бд
    def addIntoDB(self):
        cursor = connection.cursor()
        insert_query = f"INSERT INTO elements (name, specifications) VALUES ('{self.name}', '{self.specifications_string}');"
        cursor.execute(insert_query)
        connection.commit()


class Attempt:
    count_attempts = 0
    def __init__(self,  id_exp: int, func: Func, id_method: int, init: dict, result: dict):
        self.id_exp = id_exp
        self.func = func
        self.id_method = id_method
        self.init = init
        self.result = result
        Attempt.count_attempts += 1
        self.number = Attempt.count_attempts

    def addIntoGlobalDB(self):
        try:
            init_data = json.dumps(self.init)
            result_data = json.dumps(self.result)
            with (connection.cursor() as cursor):
                insert_query = f"INSERT INTO attempts (experiment_id, func, method_id, init_data, result) "\
                                f"VALUES ({str(self.id_exp)}, '{self.func.get_string()}', {str(self.id_method)}"\
                                f", '{init_data}', '{result_data}');"
                cursor.execute(insert_query)
                connection.commit()
        except Exception as ex:
            print(ex)

class Model:
    def __init__(self, name: str, equation: str, initial_data: dict):
        self.name = name
        self.equation = equation
        self.initial_data = initial_data
    
    def addIntoDB(self):
        try:
            init_data = json.dumps(self.initial_data)
            cursor = connection.cursor()
            insert_query = f"INSERT INTO models (name, equation, initial_data) VALUES ('{self.name}', '{self.equation}', '{init_data}');"
            cursor.execute(insert_query)
            connection.commit()
        except Exception as ex:
            print(ex)
    
    def updateInDB(self, model_id: int) -> bool:
        """
        Обновляет существующую модель в базе данных по заданному id.
        Возвращает True, если обновление прошло успешно, и False, если модель не найдена.
        """
        if not self.isInDB(model_id):
            return False
        
        try:
            init_data = json.dumps(self.initial_data)
            cursor = connection.cursor()
            update_query = """
                UPDATE models 
                SET name = ?, equation = ?, initial_data = ?
                WHERE id = ?
            """
            cursor.execute(update_query, 
                        (self.name, self.equation, init_data, model_id))
            connection.commit()
            return True
        except Exception as ex:
            print(f"Ошибка при обновлении модели: {ex}")
            return False

    def createFunction(self) -> Func:
        print(self.initial_data)
        print(self.equation)
        print(self.replacingExpressions())
        
        return Func(self.replacingExpressions())
    
    def replacingExpressions(self) -> str:
        new_equation = self.equation
        for item in self.initial_data.items():
            while item[0] in new_equation:
                new_equation = new_equation.replace(item[0], item[1])
        return new_equation
    
    @staticmethod
    def isInDB(model_id)  -> bool:
        cursor =  connection.cursor()
        select_query = f"SELECT id FROM models WHERE id = {model_id}"
        cursor.execute(select_query)
        rows = cursor.fetchall()
        if len(rows) == 0:
            return False
        return True



# для разбиения строки json формата в строку пользовательского формата
def crash(arr: list):
    s = str(arr).replace(', ', ',\n')
    s = s.replace('[','')
    s = s.replace(']','.')
    s = s.replace('\'', '')
    return s

# получение словаря со всеми данными из бд об элементах
def getAllElements(table_name: str):
    cursor =  connection.cursor()
    select_all_rows = f"SELECT * FROM {table_name}"
    cursor.execute(select_all_rows)
    rows = cursor.fetchall()
    for i in range(len(rows)):
        rows[i] = dict(rows[i])
    return rows


# для добавления в бд информации о попытке расчета
def addAttempt(id_exp: int, id_method: int, init: dict, result: dict):
    try:
        # init_a1, init_a2, result_a1, result_a2
        init_data = json.dumps(init)
        result_data = json.dumps(result)
        username = user_name
        cursor = connection.cursor()
        insert_query = f"INSERT INTO attempts (username, experiment_id, method_id, initial_a1, initial_a2, result_a1, result_a2) "\
                        f"VALUES ('{username}', '{str(id_exp)}', '{str(id_method)}', '{init_data}', '{result_data}', '');"
        cursor.execute(insert_query)
        connection.commit()
    except Exception as ex:
        print(ex)

# получение данных об эксперименте по его id
def getExperimentsAsID(id_exp: int):
    cursor = connection.cursor()
    select_query = "SELECT * FROM experiments WHERE id = ?"
    cursor.execute(select_query, (id_exp,))
    row = cursor.fetchone()
    return dict(row) if row else None



# Для работы с базами данных вне классов
def deleteExperiments(id_exp: int):
    cursor = connection.cursor()
    delete_query = f"DELETE FROM experiments WHERE id = {id_exp};"
    cursor.execute(delete_query)
    connection.commit()

def addArticle(name, author, year, link):
    cursor = connection.cursor()
    insert_query = f"INSERT INTO articles (name, author, year, link) VALUES ('{name}', '{author}', '{str(year)}', '{link}');"
    cursor.execute(insert_query)
    connection.commit()

def deleteArticle(num):
    cursor = connection.cursor()
    delete_query = f"DELETE FROM articles WHERE num = {str(num)};"
    cursor.execute(delete_query)
    connection.commit()

def getArticleName(article_id:int):
    cursor = connection.cursor()
    select_query = f'SELECT name FROM articles WHERE id = {article_id};'
    cursor.execute(select_query)
    res = cursor.fetchone()
    if res:
        return res['name']
    else:
        return None


# извлечение ветки элемента из базы данных
def getBranch(element_name: str)->list:
    cursor = connection.cursor()
    select_query = f"SELECT branch FROM elements WHERE name = '{element_name}'"
    cursor.execute(select_query)
    branch = cursor.fetchall()
    return branch[0]['branch'].split(';')[:-1]


def getIDsExperimentByName(element_type: str)->list:
    stree = maths.search.SearchTree()
    stree.make_all_branch()
    elements = stree.get_elements(element_type)
    print(elements)
    with connection.cursor() as cursor:
        select_query = 'SELECT id FROM experiments WHERE first_element = '
        for element in elements:
            select_query += '\'' + element + '\' OR '
        select_query += 'second_element = '
        for element in elements:
            select_query += '\'' + element + '\' OR '
        select_query = select_query[:len(select_query) - 4]
        select_query += ';'
        print(select_query)
        cursor.execute(select_query)
        res = cursor.fetchall()
        result = []
        for r in res:
            result.append(r['id'])
        return result

def bringToNormalFilter(filters:list):
    element_filter = filters.copy()
    for i in range(len(element_filter)):
        element = element_filter[i]
        element = element.lower()
        if element != 'not':
            first_letter = element[0].upper()
            element = first_letter + element[1:]
            index = element.find('-')
            if index != -1 and index != len(element) - 1:
                first_letter = element[index + 1].upper()
                element = element[:index + 1] + first_letter + element[(index+2):] 
        element_filter[i] = element
    return element_filter
    


def getElementsListByFilter(element_filter: str):
    from search.search import SEARCH_TREE
    filters_list = element_filter.split(' ')
    filters_list = bringToNormalFilter(filters_list)
    returned_list = []
    is_except = False
    for f in filters_list:
        if f == 'not':
            is_except = True
        else:
            if is_except:
                all_elements = SEARCH_TREE.get_elements('Any')
                except_elements = SEARCH_TREE.get_elements(f)
                returned_list += [i for i in all_elements if i not in except_elements]
            else:
                returned_list += SEARCH_TREE.get_elements(f)
            is_except = False
    return returned_list

def getModelByName(name: str):
    """
    Получает модель из базы данных по имени.
    Возвращает экземпляр класса Model, если модель найдена, иначе None.
    """
    try:
        cursor = connection.cursor()
        select_query = "SELECT id, name, equation, initial_data FROM models WHERE name = ?"
        cursor.execute(select_query, (name,))
        row = cursor.fetchone()
        
        if row:
            model_id, name, equation, initial_data_json = row
            initial_data = json.loads(initial_data_json)
            return Model(name, equation, initial_data), model_id
        return None, None
    except Exception as ex:
        print(f"Ошибка при получении модели по имени: {ex}")
        return None, None

def getModelById(model_id: int):
    """
    Получает модель из базы данных по id.
    Возвращает экземпляр класса Model, если модель найдена, иначе None.
    """
    try:
        cursor = connection.cursor()
        select_query = "SELECT id, name, equation, initial_data FROM models WHERE id = ?"
        cursor.execute(select_query, (model_id,))
        row = cursor.fetchone()
        
        if row:
            model_id, name, equation, initial_data_json = row
            initial_data = json.loads(initial_data_json)
            return Model(name, equation, initial_data)
        return None
    except Exception as ex:
        print(f"Ошибка при получении модели по имени: {ex}")
        return None

def getAllModelsName():
    """
    Возвращает все имена моделей, отсортированные по алфавиту
    """
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM models ORDER BY name")
    models = cursor.fetchall()
    return models


# def create_models_table():
#     cursor = connection.cursor()
#     create_table_query = "CREATE TABLE models (id int AUTO_INCREMENT, "\
#                                 "name varchar(64), "\
#                                 "equation varchar(64), "\
#                                 "initial_data, PRIMARY KEY(id));"
#     cursor.execute(create_table_query)




# table USERS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE users (id int AUTO_INCREMENT, "\
        #                          "name varchar(32), "\
        #                          "password varchar(32), "\
        #                          "email varchar(32), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table EXPERIMENTS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE experiments (id int AUTO_INCREMENT, "\
        #                          "first_element varchar(32), "\
        #                          "second_element varchar(32), "\
        #                          "temperature float(2), "\
        #                          "source_data JSON, "\
        #                          "article varchar(32), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table ELEMENTS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE elements (id int AUTO_INCREMENT, " \
        #                          "name varchar(32), " \
        #                          "specifications varchar(512), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table ATTEMPTS create
        # with connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE attempts (id int AUTO_INCREMENT, " \
        #                          "username varchar(32), " \
        #                          "experiment_id int, " \
        #                          "method_id int, " \
        #                          "initial_a1 float, " \
        #                          "initial_a2 float, " \
        #                          "result_a1 float, " \
        #                          "result_a2 float, PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)
        #
        # table ARTICLES create
        # with reliase.connection.cursor() as cursor:
        #     create_table_query = "CREATE TABLE articles (id int AUTO_INCREMENT, "\
        #                          "name varchar(64), "\
        #                          "author varchar(64), "\
        #                          "year int, "\
        #                          "link varchar(128), PRIMARY KEY(id));"
        #     cursor.execute(create_table_query)