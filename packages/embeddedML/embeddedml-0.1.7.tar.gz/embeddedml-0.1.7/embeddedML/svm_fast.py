import numpy as np
class SVMFast:
    def __init__(self):
        self.weigths = None
        self.bias = None
    def train(self, train_data_x, train_data_y, epochs=10, lr=0.01, lambda_param=0.001, beta=0.9,n=20):
        satir_sayisi, sutun_sayisi = train_data_x.shape
        self.weigths = np.zeros(sutun_sayisi)
        self.bias = 0.0
        momentum_weigths = np.zeros_like(self.weigths)
        momentum_bias = 0.0
        for i in range(epochs):
            toplam_dogru = 0
            toplam_yanlis = 0
            for j in range(satir_sayisi):
                x = train_data_x[j]
                y = train_data_y[j]
                value = y * ((x @ self.weigths) + self.bias)
                if toplam_dogru > satir_sayisi * 1 / n:
                    break
                if value > 1:
                    toplam_dogru += 1
                    gradiant_weigths = 2 * lambda_param * self.weigths
                    gradiant_bias = 0.0
                else:
                    toplam_yanlis += 1
                    gradiant_weigths = 2 * lambda_param * self.weigths - y * x
                    gradiant_bias = -y
                momentum_weigths = beta * momentum_weigths + (1 - beta) * gradiant_weigths
                momentum_bias = beta * momentum_bias + (1 - beta) * gradiant_bias
                self.weigths -= lr * momentum_weigths
                self.bias -= lr * momentum_bias
    def predict(self, test_data):
        value = np.dot(test_data, self.weigths) + self.bias
        return np.where(value > 0, 1, -1)