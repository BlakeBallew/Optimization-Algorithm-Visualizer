import numpy as np
from functions.string_eval import NumericStringParser


def compute_gradient(expression, x, y):
    nsp = NumericStringParser()
    partitions = 21
    offset = 0.01
    x_inputs = np.linspace(x-offset, x+offset, num=partitions, endpoint=True)
    y_inputs = np.linspace(y-offset, y+offset, num=partitions, endpoint=True)[::-1]
    data_points = [[0 for _ in range(len(x_inputs))] for _ in range(len(y_inputs))]
    for row in range(len(data_points)):
        for col in range(len(data_points)):
            ready_expression = expression.replace('x', str(x_inputs[col])).replace('y', str(y_inputs[row]))
            z = nsp.eval(ready_expression)
            data_points[row][col] = z
    gradient_matrix = np.gradient(data_points, x_inputs, y_inputs)
    coord = (partitions-1) // 2
    print(gradient_matrix[0][coord][coord], gradient_matrix[1][coord][coord])
    
    return gradient_matrix[0][coord][coord], gradient_matrix[1][coord][coord]
