import random
from typing import Dict, List, Tuple

from calculation.function import MathFunction
from calculation.optimizer import get_optimizer
from domain.models import Experiment, Model
from infrastructure.repositories import ExperimentRepository


class CalculationService:
    def __init__(self):
        self.experiment_repo = ExperimentRepository()

    def prepare_data(self, experiment: Experiment, model: Model) -> List[Tuple[float, float]]:
        data = []
        source = experiment.source_data
        
        arg_values = source.get(model.argument, [])
        param_values = source.get(model.calculated_parameter, [])
        
        for i in range(min(len(arg_values), len(param_values))):
            data.append((float(arg_values[i]), float(param_values[i])))
        
        return data

    def create_function(self, model: Model) -> MathFunction:
        return MathFunction(
            model.equation,
            model.calculated_parameter,
            model.argument
        )

    def optimize(
        self,
        experiment_id: int,
        model: Model,
        method_id: int,
        initial_params: Dict[str, float],
        **kwargs
    ) -> Tuple[Dict[str, float], float]:
        experiment = self.experiment_repo.get_by_id(experiment_id)
        if not experiment:
            raise ValueError(f'Experiment {experiment_id} not found')

        func = self.create_function(model)
        data = self.prepare_data(experiment, model)
        temperature = experiment.temperature or 298.15

        optimizer = get_optimizer(method_id, func, data, temperature)
        return optimizer.optimize(initial_params, **kwargs)

    def multi_start_optimize(
        self,
        experiment_id: int,
        model: Model,
        method_id: int,
        mins: Dict[str, float],
        maxs: Dict[str, float],
        count: int,
        **kwargs
    ) -> List[Dict[str, float]]:
        results = []
        
        for _ in range(count):
            random_params = {
                key: random.uniform(mins[key], maxs[key]) 
                for key in mins.keys()
            }
            
            try:
                optimized, _ = self.optimize(
                    experiment_id, 
                    model, 
                    method_id, 
                    random_params,
                    **kwargs
                )
                
                if all(mins[k] <= optimized[k] <= maxs[k] for k in optimized if k in mins):
                    results.append(optimized)
            except Exception:
                continue
        
        return results

    def generate_plot_data(
        self,
        experiment: Experiment,
        model: Model,
        optimized_params: Dict[str, float]
    ) -> Tuple[List[float], List[float], List[float], List[float]]:
        func = self.create_function(model)
        data = self.prepare_data(experiment, model)
        
        if not data:
            return [], [], [], []
        
        start, end = data[0][0], data[-1][0]
        x_model = [0] + [start + 0.005 * n for n in range(int((end - start) / 0.005) + 1) if start + 0.005 * n < end] + [1]
        
        params = {**optimized_params, 'temp': experiment.temperature or 298.15}
        y_model = [func.evaluate({**params, 'x': x}) for x in x_model]
        
        x_exp = [0] + [d[0] for d in data] + [1]
        y_exp = [0] + [d[1] for d in data] + [1]
        
        return x_model, y_model, x_exp, y_exp