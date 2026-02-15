import pandas as pd
import numpy as np

import foundation.basis as reliase

def get_experiment_from_csv(path: str):
    elements_names = pd.read_csv(path, nrows=0).columns.to_list()
    parameters = pd.read_csv(path, skiprows=[0]).columns.astype('float').to_list()
    if np.isnan(parameters[0]):
        parameters[0] = None
    if np.isnan(parameters[1]):
        parameters[1] = None

    df = pd.read_csv(path, skiprows=range(2))

    data = df.to_dict()
    for item in data.items():
        mas = []
        for i in data[item[0]].items():
            mas.append(i[1])
        data[item[0]] = mas

    return reliase.Experiment(first_element=elements_names[0], second_element=elements_names[1], 
                                 temperature=parameters[0], pressure=parameters[1], source_data=data, article=1)
    

if __name__ == '__main__':
    import os

    directory = 'articles/Excess Gibbs Free Energies at Eight Temperatures and Excess'
    files = os.listdir(directory)
    files.sort()
    for file in files:
        path = directory + '/' + file
        exp = get_experiment_from_csv(path)
        exp.add_into_db()