import numpy as np

class PolynomialRegressionFast:
    def __init__(self):
        self.coefficients=None
    def poly(self, X, degree):
        XX = []
        row = len(X)
        col = len(X[0])
        for i in range(row):
            XXX = [1]
            for j in range(0, col):
                for k in range(1, degree + 1):
                    XXX.append(X[i][j] ** k)
            for j in range(1, col):
                for k in range(j + 1, col):
                    XXX.append(X[i][j] * X[i][k])
            XX.append(XXX)
        return np.array(XX)
    def train(self,X,y,degree=3,mode=1):
        X = self.poly(X, degree)
        y = np.array(y).reshape(-1, 1)
        I = np.eye(X.shape[1])
        if mode==1:
            self.coefficients=np.dot(np.dot(np.linalg.inv(np.dot(X.T,X)+ 1e-5*I),X.T),y)
        else:

            self.coefficients = np.linalg.inv(X.T @ X + 1e-5 * I) @ X.T @ y
    def predict(self,X,degree=3):
        X=self.poly(X,degree)
        return np.dot(X,self.coefficients)
