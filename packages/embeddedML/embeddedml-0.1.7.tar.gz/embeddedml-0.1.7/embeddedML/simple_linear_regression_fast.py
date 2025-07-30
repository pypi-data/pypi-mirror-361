import numpy as np
class SimpleLinearRegressionFast:
    def __init__(self):
        self.slope=0.0
        self.intercept=0.0
    def train(self,X,y):
        length=len(y)
        self.slope=(length*np.sum(X*y)- np.sum(y)*np.sum(X))/(length*np.sum(X**2)-np.sum(X)**2)
        self.intercept=(np.sum(y)-self.slope*np.sum(X))/length
    def predict(self,X):
        return self.slope*X+self.intercept


