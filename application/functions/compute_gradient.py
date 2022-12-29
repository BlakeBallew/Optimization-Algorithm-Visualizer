import numpy as np
from functions.string_eval import NumericStringParser

nsp = NumericStringParser()

def compute_gradient(expression, x_range, y_range, x, y, partitions):
    partitions = 41
    x_inputs = np.linspace(x-1, x+1, num=41, endpoint=True)
    y_inputs = np.linspace(y-1, y+1, num=41, endpoint=True)[::-1]
    data_points = [[0 for _ in range(len(x_inputs))] for _ in range(len(y_inputs))]
    for x in range(partitions):
        for y in range(partitions):
            ready_expression = expression.replace('x', str(x_inputs[y])).replace('y', str(y_inputs[x]))
            z = nsp.eval(ready_expression)
            data_points[x][y] = z

    # print(x_inputs)
    # print(y_inputs)
    gradient_matrix = np.gradient(data_points, x_inputs, y_inputs)

    # print(gradient_matrix[0][20][20], gradient_matrix[1][20][20])   
    # print([np.gradient(data_points, x_inputs, y_inputs)[0][50][50], np.gradient(data_points, x_inputs, y_inputs)[1][50][50]])
    return data_points