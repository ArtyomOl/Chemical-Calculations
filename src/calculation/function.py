from typing import Any, Dict

import sympy as sp


class MathFunction:
    def __init__(self, expression: str, calculated_param: str, argument: str):
        self.expression = expression
        self.calculated_param = calculated_param
        self.argument = argument
        self.symbolic_expr = sp.sympify(expression)
        self._derivatives_cache: Dict[str, Any] = {}
        self._second_derivatives_cache: Dict[tuple, Any] = {}

    def evaluate(self, params: Dict[str, float]) -> float:
        value = self.symbolic_expr.subs(params)
        return float(value.evalf())

    def derivative(self, variable: str, params: Dict[str, float]) -> float:
        if variable not in self._derivatives_cache:
            var = sp.symbols(variable)
            self._derivatives_cache[variable] = sp.diff(self.symbolic_expr, var)
        
        deriv_expr = self._derivatives_cache[variable]
        value = deriv_expr.subs(params)
        return float(value.evalf())

    def second_derivative(self, var1: str, var2: str, params: Dict[str, float]) -> float:
        key = (var1, var2)
        
        if key not in self._second_derivatives_cache:
            if var1 not in self._derivatives_cache:
                symbol1 = sp.symbols(var1)
                self._derivatives_cache[var1] = sp.diff(self.symbolic_expr, symbol1)
            
            symbol2 = sp.symbols(var2)
            self._second_derivatives_cache[key] = sp.diff(
                self._derivatives_cache[var1], 
                symbol2
            )
        
        second_deriv_expr = self._second_derivatives_cache[key]
        value = second_deriv_expr.subs(params)
        return float(value.evalf())