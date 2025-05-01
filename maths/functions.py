import decimal as dc
from sympy import *

class Func:
    def __init__(self, function_string: str = '', calculated_parameter: str = '') -> None:
        self.function_string = function_string
        self.compiled_expression = compile(self.function_string, '<string>', 'eval')
        self.symbolic_expression = sympify(function_string)
        self.calculated_parameter = calculated_parameter
        

    def get_string(self):
        return self.function_string

    def result(self, initial_params: dict[str, any] = None):
        if initial_params is None:
            initial_params = {}
        return eval(self.compiled_expression, globals(), initial_params)

    def derivative(self, variable: str, point: dict[str, any]):
        var = symbols(variable)
        derivative_expr = diff(self.symbolic_expression, var)
        derivative_value = derivative_expr.subs(point)
        return derivative_value.evalf()

    def second_derivative(self, first_variable: str, second_variable: str, point: dict[str, any]):
        var1 = symbols(first_variable)
        var2 = symbols(second_variable)
        first_derivative = diff(self.symbolic_expression, var1)
        second_derivative = diff(first_derivative, var2)
        second_derivative_value = second_derivative.subs(point)
        return second_derivative_value.evalf()

    @staticmethod
    def margulis(a1, a2, x, temp):
        D = dc.Decimal
        return D(D(8.31) * D(temp) * D(x) * (1 - D(x)) * ((1 - D(x)) * D(a1) + D(a2) * D(x)))
    


# margulis = Func("8.31 * temp * x * (1 - x) * ((1 - x) * a12 + a21 * x)")
