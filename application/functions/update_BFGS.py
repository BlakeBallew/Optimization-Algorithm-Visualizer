import numpy as np
"""
Created on Sat Dec 18 12:29:06 2021
@author: Dr. Edoh Amiran edoh@wwu.edu
A single update of the matrix for the BFGS method. 
Input is the previous matrix, the change in the gradient, and 
the change in the variable. 
Parameters
----------
M is an n by n martix, as an array of shape (n,n) 
It is assumed that M is symmetric 
cg and cx are arrays of length/size n
Returns
-------
H is expected as an array of shape (n,n) 
"""

def update_BFGS(M,cg,cx):
    n=len(cx)
    den = np.dot(cg,cx)
    u=np.reshape(cx,(1,n))  # might not be necessary
    s=np.reshape(cx,(n,1))  # might not be necessary
    v = np.dot(M,cg)
    factor = np.dot(cg,v)
    t=np.reshape(v,(1,n))   # might not be necessary
    w=np.reshape(v,(n,1))   # might not be necessary
    H = M + (1/den)*(1+factor/den)*np.dot(s,u)
    P = np.dot(w,u) + np.dot(s,t)
    P = P/den
    H = H - P
    return H