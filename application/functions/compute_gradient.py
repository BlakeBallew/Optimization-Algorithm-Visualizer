import numpy as np
from functions.string_eval import NumericStringParser

nsp = NumericStringParser()

def compute_gradient(expression, x, y):
    partitions = 21
    x_inputs = np.linspace(x-0.01, x+0.01, num=partitions, endpoint=True)
    y_inputs = np.linspace(y-0.01, y+0.01, num=partitions, endpoint=True)[::-1]
    data_points = [[0 for _ in range(len(x_inputs))] for _ in range(len(y_inputs))]
    for x in range(partitions):
        for y in range(partitions):
            ready_expression = expression.replace('x', str(x_inputs[y])).replace('y', str(y_inputs[x]))
            z = nsp.eval(ready_expression)
            data_points[x][y] = z

    gradient_matrix = np.gradient(data_points, x_inputs, y_inputs)

    coord = (partitions-1) // 2

    return gradient_matrix[0][coord][coord], gradient_matrix[1][coord][coord]  
