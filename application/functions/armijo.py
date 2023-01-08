import numpy as np

"""
Spyder Editor
created by Dr. Edoh Amiran, December 15, 2021. edoh@wwu.edu
a>0, 0<r<1, 0<c<1, p is the direction, y is f(x_k), g is the gradient
psi(a) is f(x_k+a*p), which must be available 
returns the value of a decided by the Armijo condition
"""

def armijo_search(desc_dir, y, grad, func):
    a = .4
    r = .6
    c = .01    

    b=c*np.dot(grad, desc_dir)
    while(func(a, desc_dir)>y+a*b):
        if(np.linalg.norm(a*desc_dir)<.01):           #quit if norm of gradient gets too small
            return a
        a=r*a
    return a

