import numpy as np
from functions.string_eval import NumericStringParser

nsp = NumericStringParser()

def compute_zmatrix(expression, x_range, y_range, partitions):
    x_inputs = np.linspace(x_range[0], x_range[1], num=partitions, endpoint=True)
    y_inputs = np.linspace(y_range[0], y_range[1], num=partitions, endpoint=True)[::-1]
    zmatrix = [[0 for _ in range(len(x_inputs))] for _ in range(len(y_inputs))]

    for x in range(partitions):
        for y in range(partitions):
            ready_expression = expression.replace('x', str(x_inputs[y])).replace('y', str(y_inputs[x]))
            z = nsp.eval(ready_expression)
            zmatrix[x][y] = z

    return x_inputs, y_inputs, zmatrix