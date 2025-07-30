import numpy as np

class KNNFast:
    def predict(self,X,y,Test_data,k):
        predictions=[]
        for test_data in Test_data:
            diff_X=X-test_data
            squared_diff=np.sum(diff_X**2,axis=1)
            sqrt_diff=np.sqrt(squared_diff)
            indices=np.argsort(sqrt_diff)[:k]
            neighbours=y[indices]
            value=np.sum(neighbours)/len(neighbours)
            if value>0.5:
                predictions.append(1)
            else:
                predictions.append(0)
        return np.array(predictions)
