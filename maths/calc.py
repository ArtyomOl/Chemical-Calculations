import random
from typing import *

from maths.methods import *

def simple_calculation(experiment_id: int, init_data: dict[str, float], method_num: int, used_function: Optional[str]=None):
    print('call simple_calculation')
    method = get_method(used_function, method_num, experiment_id)
    result, _ = method.calculate(init_data)
    return result


def multi_start(id_exp: int, mins: dict[float], maxs: dict[float], count: int, method_num: int, used_function=None):
    method = get_method(used_function, method_num, id_exp)
    result = []
    for i in range(count):
        random_params = {}
        for key in mins.keys():
            random_params[key] = random.uniform(mins[key], maxs[key])
        new_params, _ = method.calculate(random_params)
        if all(mins[key] <= new_params[key] <= maxs[key] for key in new_params.keys()):
            result.append(new_params)
    return result
