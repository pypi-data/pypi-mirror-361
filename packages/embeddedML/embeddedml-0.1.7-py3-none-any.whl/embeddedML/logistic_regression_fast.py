import numpy as np

class LogisticRegressionFast:
    def __init__(self):
        self.weights = None
        self.bias = 0.0
    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))
    def predict_proba(self, X):
        return self.sigmoid(np.dot(X, self.weights) + self.bias)
    def predict(self, X):
        proba = self.predict_proba(X)
        return (proba >= 0.5).astype(int)
    def train(self, X, y, epochs=10, lr=0.1, beta1=0.9, beta2=0.999, epsilon=1e-8):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0.0
        m_w = np.zeros(n_features)  # Momentum (ilk moment)
        v_w = np.zeros(n_features)  # RMS (ikinci moment)
        m_b = 0.0
        v_b = 0.0
        for t in range(1, epochs + 1):
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)
            dw =  np.dot(X.T, (y - y_predicted))
            db =  np.sum(y - y_predicted)
            m_w = beta1 * m_w + (1 - beta1) * dw
            m_b = beta1 * m_b + (1 - beta1) * db
            v_w = beta2 * v_w + (1 - beta2) * (dw ** 2)
            v_b = beta2 * v_b + (1 - beta2) * (db ** 2)
            m_w_corr = m_w / (1 - beta1 ** t)
            m_b_corr = m_b / (1 - beta1 ** t)
            v_w_corr = v_w / (1 - beta2 ** t)
            v_b_corr = v_b / (1 - beta2 ** t)
            self.weights += lr * m_w_corr / (np.sqrt(v_w_corr) + epsilon)
            self.bias += lr * m_b_corr / (np.sqrt(v_b_corr) + epsilon)
    def evaluate(self, X, y):
        y_pred = self.predict(X)
        accuracy = np.mean(y_pred == y) * 100
        return accuracy



