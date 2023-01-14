import numpy as np
from functions.string_eval import NumericStringParser

# adapted from code provided by user @rth via stackoverflow.com
# link: https://stackoverflow.com/questions/31206443/numpy-second-derivative-of-a-ndimensional-array
def hessian(x: np.array) -> np.array:
    x_grad = np.gradient(x) 
    hessian = np.empty((x.ndim, x.ndim) + x.shape, dtype=x.dtype) 
    for k, grad_k in enumerate(x_grad):
        tmp_grad = np.gradient(grad_k) 
        for l, grad_kl in enumerate(tmp_grad):
            hessian[k, l, :, :] = grad_kl
    return hessian

def compute_hessian(expression: str, x: int, y: int) -> np.array:
    nsp = NumericStringParser()
    partitions = 11
    x_inputs = np.linspace(x-5, x+5, num=partitions, endpoint=True).tolist()
    y_inputs = np.linspace(y-5, y+5, num=partitions, endpoint=True).tolist()[::-1]
    data_points = [[0 for _ in range(len(x_inputs))] for _ in range(len(y_inputs))]
    for row in range(len(data_points)):
        for col in range(len(data_points)):
            ready_expression = expression.replace('x', str(x_inputs[col])).replace('y', str(y_inputs[row]))
            z = nsp.eval(ready_expression)
            data_points[row][col] = z
    
    coord = (partitions - 1) // 2
    data_points_numpy = np.array(data_points)
    hessian_info = hessian(data_points_numpy)
    hessian_matrix = np.array([[hessian_info[1][1][coord][coord], -hessian_info[0][1][coord][coord]], [-hessian_info[1][0][coord][coord], hessian_info[0][0][coord][coord]]])
    hessian_matrix_inverse = np.linalg.inv(hessian_matrix)
    
    return hessian_matrix_inverse