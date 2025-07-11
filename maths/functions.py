import decimal as dc
from sympy import *

class Func:
    def __init__(self, function_string: str = '', calculated_parameter: str = '', argument: str = '') -> None:
        self.function_string = function_string
        self.compiled_expression = compile(self.function_string, '<string>', 'eval')
        self.symbolic_expression = sympify(function_string)
        self.calculated_parameter = calculated_parameter
        self.argument = argument
        
        # Кэшируем символьные переменные и пыроизводные
        self._symbols_cache = {}
        self._first_derivatives = {}
        self._second_derivatives = {}
        
    def get_string(self):
        return self.function_string

    def result(self, initial_params: dict[str, any] = None):
        if initial_params is None:
            initial_params = {}
        return eval(self.compiled_expression, globals(), initial_params)

    def derivative(self, variable: str, point: dict[str, any]):
        # Проверяем кэш
        if variable not in self._first_derivatives:
            var = symbols(variable)
            self._symbols_cache[variable] = var
            self._first_derivatives[variable] = diff(self.symbolic_expression, var)
        
        # Получаем производную из кэша и подставляем значения
        derivative_expr = self._first_derivatives[variable]
        derivative_value = derivative_expr.subs(point)
        return derivative_value.evalf()

    def second_derivative(self, first_variable: str, second_variable: str, point: dict[str, any]):
        # Создаем ключ для кэша вторых производных
        key = (first_variable, second_variable)
        
        # Проверяем кэш
        if key not in self._second_derivatives:
            # Убедимся, что символы есть в кэше
            if first_variable not in self._symbols_cache:
                self._symbols_cache[first_variable] = symbols(first_variable)
            if second_variable not in self._symbols_cache:
                self._symbols_cache[second_variable] = symbols(second_variable)
                
            # Вычисляем производные (если первой производной нет - вычислим и её)
            if first_variable not in self._first_derivatives:
                self._first_derivatives[first_variable] = diff(
                    self.symbolic_expression, 
                    self._symbols_cache[first_variable]
                )
                
            # Вычисляем вторую производную
            self._second_derivatives[key] = diff(
                self._first_derivatives[first_variable],
                self._symbols_cache[second_variable]
            )
        
        # Получаем вторую производную из кэша и подставляем значения
        second_derivative_expr = self._second_derivatives[key]
        second_derivative_value = second_derivative_expr.subs(point)
        return second_derivative_value.evalf()

    @staticmethod
    def margulis(a1, a2, x, temp):
        D = dc.Decimal
        return D(D(8.31) * D(temp) * D(x) * (1 - D(x)) * ((1 - D(x)) * D(a1) + D(a2) * D(x)))