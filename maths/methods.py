import abc
import matplotlib.pyplot as plt
import json
import math
import random
import sympy
from abc import abstractmethod
import decimal as dc

import foundation.basis
import maths.functions
from maths.functions import Func
from matplotlib.pyplot import figure


D = dc.Decimal
R = (8.31)

# абстрактный класс - для обобщения всех используемых методов
class Method(abc.ABC):
    def __init__(self, id_exp: int, used_function: Func):
        self.id_exp = id_exp
        self.used_function = used_function
        self.experiment_data = foundation.basis.getExperimentAsID(id_exp)
        self.data = self.make_list(self.id_exp)
        self.temp = self.experiment_data['temperature']
    
    # def margulis(self, a1, a2, x, temp):
    #     return R * (temp) * (x) * (1 - (x)) * ((1 - (x)) * (a1) + (a2) * (x))
    
    def model_result(self, initial_params: dict[str, float]):
        return (float(self.used_function.result(initial_params)))
    def model_deriative(self,variable:str,point:dict[str, float]):
        return (float(self.used_function.derivative(variable,point)))
    def model_second_deriative(self,first_variable:str,second_variable:str,point:dict[str, float]):
        return (float(self.used_function.second_derivative(first_variable,second_variable,point)))

    def minimum(self, gej: float, initial_params: dict[str, float], x: float) -> dc.Decimal:
        params = initial_params.copy()
        params['x'] = x
        params['temp'] = self.temp
        return (((gej)) - self.model_result(params)) ** 2
    def minimum_deriative(self, gej: float, initial_params: dict[str, float], x: float, variable: str) -> dc.Decimal:
        params = initial_params.copy()
        params['x'] = x
        params['temp'] = self.temp
        return self.model_deriative(variable, params) * 2 * (((gej)) - self.model_result(params))
    def minimum_second_deriative(self, gej: float, initial_params: dict[str, float], x: float, first_variable: str, second_variable: str) -> dc.Decimal:
        params = initial_params.copy()
        params['x'] = x
        params['temp'] = self.temp
        return 2 * self.model_second_deriative(first_variable,second_variable, params) * \
                (((gej)) - self.model_result(params)) - \
                2 * self.model_deriative(first_variable,params) * self.model_deriative(second_variable,params)

    def minimum_sum(self, initial_params: dict[str, float]) -> dc.Decimal:
        return sum(self.minimum(gej, initial_params, x) for x, gej in self.data)
    def minimum_deriative_sum(self, initial_params: dict[str, float], variable:str) -> dc.Decimal:
        return sum(self.minimum_deriative(gej, initial_params, x, variable) for x, gej in self.data)
    def minimum_second_deriative_sum(self, initial_params: dict[str, float],first_variable:str, second_variable:str) -> dc.Decimal:
        return sum(self.minimum_second_deriative(gej, initial_params, x,first_variable,second_variable) for x, gej in self.data)
    
    def H(self, initial_params: dict[str,float]):
        matr_doc = {}
        for i in range(0, len(initial_params)):
            for j in range(0, len(initial_params)):
                matr_doc[i,j]=0
        i=0
        j=0
        for key1 in initial_params:
                j=0
                for key2 in initial_params:
                    matr_doc[i,j]=self.minimum_second_deriative_sum(initial_params,key1,key2)
                    j+=1
                i+=1
        h=sympy.SparseMatrix.from_dok(len(initial_params),len(initial_params),matr_doc)
        #h=sympy.Matrix
        #h.from_dok(len(initial_params),len(initial_params),matr_doc)
        h=h.inv()
        return h
    

    def gr(self, initial_params: dict[str,float]):
        matr_doc = {}
        for i in range(0, len(initial_params)):
            matr_doc[i,0]=0
        i=0
        j=0
        for key1 in initial_params:
                matr_doc[i,0]=float(self.minimum_deriative_sum(initial_params,key1))
                i+=1
        h=sympy.SparseMatrix.from_dok(len(initial_params),1,matr_doc)
        return h

    @abstractmethod
    def calculate(self, initial_data: dict[str, float]): pass

    def make_list(self, id_exp):
        experiment = foundation.basis.getExperimentAsID(id_exp)
        source_data = json.loads(experiment['source_data'])
        result = []
        for i in range(min(len(source_data[self.used_function.argument]), len(source_data[self.used_function.calculated_parameter]))):
            result.append([float(source_data[self.used_function.argument][i]), float(source_data[self.used_function.calculated_parameter][i])])
        return result


    def draw_chart(self, initial_data: dict[str, float], ax=None):
        arr = self.make_list(self.id_exp)

        result,_ = self.calculate(initial_data)

        t = foundation.basis.getExperimentAsID(self.id_exp)['temperature']
        start, end = arr[0][0], arr[-1][0]
        x = [0] + [i for i in [start + 0.005 * n for n in range(int((end - start) / 0.005) + 1)] if i < end] + [1]
        
        # Расчет y значений
        result['temp'] = self.temp
        y = [self.model_result({**result, 'x': x2}) for x2 in x]

        x2 = [arr[i][0] for i in range(len(arr))]
        x2 = [0] + x2 + [1]
        y2 = [arr[i][1] for i in range(len(arr))]
        y2 = [0] + y2 + [1]

        plt.plot(x, y)
        plt.xlabel('x2')  # Подпись для оси х
        plt.ylabel(self.used_function.calculated_parameter)  # Подпись для оси y
        plt.title('T = ' + str(t))  # Название
        plt.plot(x, y, color='green', marker='o', markersize=0.01)
        plt.plot(x2, y2, color='red', marker='o', markersize=7, linestyle='')
        plt.grid()
        #plt.show()
        ax = plt



# метод имитации отжига
class MethodOfSimulatedAnnealing(Method):
    def __init__(self, id_exp: int, used_function: Func = None):
        super().__init__(id_exp, used_function)

    @staticmethod
    def temperature(k):
        return 10 / math.log(1 + k)

    @staticmethod
    def neighbour(a, t):
        return a + (random.random() * t - t / 2)

    @staticmethod
    def acceptanceProbability(old, new, t):
        if new < old:
            return 1.0
        try:
            return math.exp((old - new) / t)
        except OverflowError:
            return 0.0

    def calculate(self, initial_data: dict[str, float], max_iterations: int = 10000, initial_temperature: float = 100.0) -> tuple[dict[str, float], float]:
        current_params = initial_data.copy()
        best_params = current_params.copy()
        best_value = self.minimum_sum(best_params)

        for iteration in range(1, max_iterations + 1):
            t = self.temperature(iteration)
            new_params = {key: self.neighbour(value, t) for key, value in current_params.items()}
            new_value = self.minimum_sum(new_params)

            if self.acceptanceProbability(float(best_value), float(new_value), t) >= random.random():
                current_params = new_params
                if new_value < best_value:
                    best_params = new_params.copy()
                    best_value = new_value

        return best_params, float(best_value)


# метод Гаусса - Зейделя
class MethodGaussZeidel(Method):
    def __init__(self, id_exp: int, used_function: Func = None):
        super().__init__(id_exp, used_function)

    def calculate(self, initial_data: dict[str, float], max_iterations: int = 1000, tolerance: float = 1e-6) -> tuple[dict[str, float], float]:
        current_params = initial_data.copy()
        step_sizes = {key: 1.0 for key in current_params}  # Начальные шаги для каждого параметра
        best_params = current_params.copy()
        best_value = self.minimum_sum(best_params)

        for iteration in range(max_iterations):
            for key in current_params:
                # Пробуем увеличить параметр
                current_params[key] += step_sizes[key]
                new_value = self.minimum_sum(current_params)
                if new_value < best_value:
                    best_value = new_value
                    best_params = current_params.copy()
                else:
                    # Пробуем уменьшить параметр
                    current_params[key] -= 2 * step_sizes[key]
                    new_value = self.minimum_sum(current_params)
                    if new_value < best_value:
                        best_value = new_value
                        best_params = current_params.copy()
                    else:
                        # Возвращаем исходное значение и уменьшаем шаг
                        current_params[key] += step_sizes[key]
                        step_sizes[key] /= 2

            # Проверка на сходимость
            if all(size < tolerance for size in step_sizes.values()):
                break

        return best_params, float(best_value)

# метод Хукка - Дживса
class MethodHookJeeves(Method):
    def __init__(self, id_exp: int, used_function: Func = None):
        super().__init__(id_exp, used_function)

    def calculate(self, initial_data: dict[str, float], step_size: float = 1.0, tolerance: float = 1e-6) -> tuple[dict, float]:
        current_params = {key: float(value) for key, value in initial_data.items()}
        best_params = current_params.copy()
        best_value = float(self.minimum_sum(best_params))

        while step_size > tolerance:
            # Исследовательский поиск
            improved = False
            for key in current_params:
                original_value = current_params[key]

                # Пробуем увеличить параметр
                current_params[key] = original_value + step_size
                new_value = float(self.minimum_sum(current_params))
                if new_value < best_value:
                    best_value = new_value
                    best_params = current_params.copy()
                    improved = True
                else:
                    # Пробуем уменьшить параметр
                    current_params[key] = original_value - step_size
                    new_value = float(self.minimum_sum(current_params))
                    if new_value < best_value:
                        best_value = new_value
                        best_params = current_params.copy()
                        improved = True
                    else:
                        # Возвращаем исходное значение
                        current_params[key] = original_value

            # Если улучшений нет, уменьшаем шаг
            if not improved:
                step_size /= 2

        return (
            best_params,
            round(best_value, 5)
        )

# метод антиградиента
class MethodAntigradient(Method):
    def __init__(self, id_exp: int, used_function: Func = None):
        super().__init__(id_exp, used_function)
    
    def calculate(self, initial_data: dict[str, float]):
        current_params = {key: float(value) for key, value in initial_data.items()}
        best_params = current_params.copy()
        cnt = 0
        eps = (10 ** (-6))
        lam = (10 ** (-7))
        while (cnt == 0) or (abs(self.minimum_sum(current_params)) - self.minimum_sum(best_params)) > eps:
            cnt += 1
            if self.minimum_sum(best_params) > self.minimum_sum(current_params):
                lam /= 2
                lam2 /= 2
            current_params = best_params.copy()
            for key in best_params:
                best_params[key]=best_params[key] + lam * float(self.minimum_deriative_sum(best_params,key))
        return best_params, float(round(self.minimum_sum(best_params), 5))

# метод Ньютона
class MethodNewton(Method):
    def __init__(self, id_exp: int, used_function: Func = None):
        super().__init__(id_exp, used_function)
    
    def calculate(self, initial_data: dict[str, float]):
        current_params = {key: float(value) for key, value in initial_data.items()}
        best_params = current_params.copy()
        cnt = 0
        eps = 10 ** (-6)
        while (cnt == 0) or (abs(self.minimum_sum(current_params)) - self.minimum_sum(best_params)) > eps:
            cnt += 1
            current_params = best_params.copy()
            InvH = self.H(current_params)
            gra = self.gr(current_params)
            plus=InvH*gra
            i=0
            for key in best_params:
                best_params[key]=best_params[key] - plus[i]
                i+=1
        return best_params, float(round(self.minimum_sum(best_params), 5))


def get_method(used_function: Func = None, method_num: int = 0, id_exp: int = 0):
    method = None
    match method_num:
        case 0:
            method = MethodOfSimulatedAnnealing(id_exp, used_function)
        case 1:
            method = MethodGaussZeidel(id_exp, used_function)
        case 2:
            method = MethodHookJeeves(id_exp, used_function)
        case 3:
            method = MethodAntigradient(id_exp, used_function)
        case 4:
            method = MethodNewton(id_exp, used_function)
    return method


if __name__ == '__main__':
    initial_data = {'a12': 0, 'a21': 0}

    method = MethodOfSimulatedAnnealing(1, maths.functions.margulis)
    res, minimum = method.calculate(initial_data)
    print(res,minimum)

    method = MethodGaussZeidel(1, maths.functions.margulis)
    res, minimum = method.calculate(initial_data)
    print(res,minimum)

    method = MethodHookJeeves(1, maths.functions.margulis)
    res, minimum = method.calculate(initial_data)
    print(res,minimum)

    method = MethodAntigradient(1, maths.functions.margulis)
    res, minimum = method.calculate(initial_data)
    print(res,minimum)

    method = MethodNewton(1, maths.functions.margulis)
    res, minimum = method.calculate(initial_data)
    print(res,minimum)