import numpy as np

class MultipleLinearRegressionFast:
    def __init__(self):
        self.coefficients=None
    def train(self,X,y,mode=1):
        ones=np.ones((X.shape[0],1))
        X=np.hstack((ones,X))
        y=np.array(y).reshape(-1,1)
        if mode==1:
            self.coefficients=np.dot(np.dot(np.linalg.inv(np.dot(X.T,X)),X.T),y)
        else:
            self.coefficients=(np.linalg.inv(X.T@X)@X.T)@y
    def predict(self,X):
        ones=np.ones((X.shape[0],1))
        X=np.hstack((ones,X))
        return np.dot(X,self.coefficients)
