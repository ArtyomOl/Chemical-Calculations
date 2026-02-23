import math
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

import sympy

from calculation.function import MathFunction


class OptimizationMethod(ABC):
    def __init__(self, func: MathFunction, data: List[Tuple[float, float]], temperature: float):
        self.func = func
        self.data = data
        self.temperature = temperature

    def objective(self, params: Dict[str, float], x: float, target: float) -> float:
        eval_params = {**params, 'x': x, 'temp': self.temperature}
        predicted = self.func.evaluate(eval_params)
        return (target - predicted) ** 2

    def objective_sum(self, params: Dict[str, float]) -> float:
        return sum(self.objective(params, x, y) for x, y in self.data)

    def gradient_component(self, params: Dict[str, float], variable: str) -> float:
        total = 0.0
        for x, target in self.data:
            eval_params = {**params, 'x': x, 'temp': self.temperature}
            predicted = self.func.evaluate(eval_params)
            deriv = self.func.derivative(variable, eval_params)
            total += 2 * deriv * (target - predicted)
        return total

    def hessian_component(self, params: Dict[str, float], var1: str, var2: str) -> float:
        total = 0.0
        for x, target in self.data:
            eval_params = {**params, 'x': x, 'temp': self.temperature}
            predicted = self.func.evaluate(eval_params)
            second_deriv = self.func.second_derivative(var1, var2, eval_params)
            deriv1 = self.func.derivative(var1, eval_params)
            deriv2 = self.func.derivative(var2, eval_params)
            total += 2 * second_deriv * (target - predicted) - 2 * deriv1 * deriv2
        return total

    @abstractmethod
    def optimize(self, initial_params: Dict[str, float], **kwargs) -> Tuple[Dict[str, float], float]:
        pass


class SimulatedAnnealing(OptimizationMethod):
    @staticmethod
    def temperature_schedule(iteration: int) -> float:
        return 10 / math.log(1 + iteration)

    @staticmethod
    def neighbor(value: float, temp: float) -> float:
        return value + (random.random() * temp - temp / 2)

    @staticmethod
    def acceptance_probability(old_cost: float, new_cost: float, temp: float) -> float:
        if new_cost < old_cost:
            return 1.0
        try:
            return math.exp((old_cost - new_cost) / temp)
        except OverflowError:
            return 0.0

    def optimize(self, initial_params: Dict[str, float], max_iterations: int = 10000, **kwargs) -> Tuple[Dict[str, float], float]:
        current = initial_params.copy()
        best = current.copy()
        best_cost = self.objective_sum(best)

        for iteration in range(1, max_iterations + 1):
            temp = self.temperature_schedule(iteration)
            new = {k: self.neighbor(v, temp) for k, v in current.items()}
            new_cost = self.objective_sum(new)

            if self.acceptance_probability(best_cost, new_cost, temp) >= random.random():
                current = new
                if new_cost < best_cost:
                    best = new.copy()
                    best_cost = new_cost

        return best, best_cost


class GaussSeidel(OptimizationMethod):
    def optimize(self, initial_params: Dict[str, float], max_iterations: int = 1000, tolerance: float = 1e-6, **kwargs) -> Tuple[Dict[str, float], float]:
        current = initial_params.copy()
        step_sizes = {k: 1.0 for k in current}
        best = current.copy()
        best_cost = self.objective_sum(best)

        for _ in range(max_iterations):
            for key in current:
                current[key] += step_sizes[key]
                new_cost = self.objective_sum(current)
                
                if new_cost < best_cost:
                    best_cost = new_cost
                    best = current.copy()
                else:
                    current[key] -= 2 * step_sizes[key]
                    new_cost = self.objective_sum(current)
                    
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best = current.copy()
                    else:
                        current[key] += step_sizes[key]
                        step_sizes[key] /= 2

            if all(size < tolerance for size in step_sizes.values()):
                break

        return best, best_cost


class HookeJeeves(OptimizationMethod):
    def optimize(self, initial_params: Dict[str, float], step_size: float = 1.0, tolerance: float = 1e-6, **kwargs) -> Tuple[Dict[str, float], float]:
        current = initial_params.copy()
        best = current.copy()
        best_cost = self.objective_sum(best)

        while step_size > tolerance:
            improved = False
            
            for key in current:
                original = current[key]
                
                current[key] = original + step_size
                new_cost = self.objective_sum(current)
                
                if new_cost < best_cost:
                    best_cost = new_cost
                    best = current.copy()
                    improved = True
                else:
                    current[key] = original - step_size
                    new_cost = self.objective_sum(current)
                    
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best = current.copy()
                        improved = True
                    else:
                        current[key] = original

            if not improved:
                step_size /= 2

        return best, best_cost


class GradientDescent(OptimizationMethod):
    def optimize(self, initial_params: Dict[str, float], max_iterations: int = 5000, learning_rate: float = 1e-3, tolerance: float = 1e-6, **kwargs) -> Tuple[Dict[str, float], float]:
        params = initial_params.copy()
        prev_cost = self.objective_sum(params)
        lr = learning_rate

        for _ in range(max_iterations):
            gradient = {k: self.gradient_component(params, k) for k in params}
            
            for k in params:
                params[k] -= lr * gradient[k]
            
            cost = self.objective_sum(params)
            
            if abs(prev_cost - cost) < tolerance:
                break
            
            if cost > prev_cost:
                lr *= 0.5
            else:
                prev_cost = cost

        return params, self.objective_sum(params)


class NewtonMethod(OptimizationMethod):
    def optimize(self, initial_params: Dict[str, float], max_iterations: int = 100, tolerance: float = 1e-6, **kwargs) -> Tuple[Dict[str, float], float]:
        current = initial_params.copy()
        
        for _ in range(max_iterations):
            prev_cost = self.objective_sum(current)
            
            hessian_dict = {}
            for i, key1 in enumerate(current):
                for j, key2 in enumerate(current):
                    hessian_dict[i, j] = self.hessian_component(current, key1, key2)
            
            hessian = sympy.SparseMatrix.from_dok(len(current), len(current), hessian_dict)
            
            try:
                inv_hessian = hessian.inv()
            except:
                break
            
            gradient_dict = {}
            for i, key in enumerate(current):
                gradient_dict[i, 0] = self.gradient_component(current, key)
            
            gradient = sympy.SparseMatrix.from_dok(len(current), 1, gradient_dict)
            delta = inv_hessian * gradient
            
            for i, key in enumerate(current):
                current[key] -= float(delta[i])
            
            new_cost = self.objective_sum(current)
            
            if abs(prev_cost - new_cost) < tolerance:
                break

        return current, self.objective_sum(current)


OPTIMIZATION_METHODS = {
    0: SimulatedAnnealing,
    1: GaussSeidel,
    2: HookeJeeves,
    3: GradientDescent,
    4: NewtonMethod,
}


def get_optimizer(method_id: int, func: MathFunction, data: List[Tuple[float, float]], temperature: float) -> OptimizationMethod:
    method_class = OPTIMIZATION_METHODS.get(method_id, SimulatedAnnealing)
    return method_class(func, data, temperature)