import random
import numpy as np
class Preprocessing:
    def min_max_scaler(self,liste,fast=True):
        length2=len(liste[0])
        if fast==False:
            for i in range(length2-1):# length2-1
                col=[j[i] for j in liste]
                min_col,max_col=min(col),max(col)
                if max_col==min_col:
                    continue
                for k in liste:
                    k[i]=(k[i]-min_col)/(max_col-min_col)
            return liste
        else:
            for i in range(length2):
                col=[j[i] for j in liste]
                min_col,max_col=min(col),max(col)
                if max_col==min_col:
                    continue
                for k in liste:
                    k[i]=(k[i]-min_col)/(max_col-min_col)
            return liste
    def standard_scaler(self, liste,fast=True):
        length2 = len(liste[0])
        if fast==True:
            for i in range(length2):
                col = [j[i] for j in liste]
                mean = sum(col) / len(col)
                std = (sum((x - mean) ** 2 for x in col) / len(col)) ** 0.5
                if std == 0:
                    continue
                for k in liste:
                    k[i] = (k[i] - mean) / std
            return np.array(liste)
        else:
            for i in range(length2-1):
                col = [j[i] for j in liste]
                mean = sum(col) / len(col)
                std = (sum((x - mean) ** 2 for x in col) / len(col)) ** 0.5
                if std == 0:
                    continue
                for k in liste:
                    k[i] = (k[i] - mean) / std
            return liste
    def poly_for_svm(self,data,degree):
        col=len(data[0])
        row=len(data)
        XX=[]
        for i in range(row):
            X=[]
            for j in range(col):
                for k in range(1,degree+1):
                    X.append(data[i][j]**k)
            for j in range(col):
                for p in range(col):
                    if j!=p:
                        X.append(data[i][j]*data[i][p])
            XX.append(X)
        return XX
    def label_transformation(self,labels):
        return [1 if int(label)==1 else -1 for label in labels]
    def train_validation_split(self,data,train_rate=0.7,fast=True,is_shuffle=True):
        length=len(data)
        if is_shuffle==True:
            random.shuffle(data)
        train_dataset=data[:int(length*train_rate)]
        validation_dataset=data[int(length*train_rate):]
        if fast==True:
            return np.array(train_dataset),np.array(validation_dataset)
        else:
            return train_dataset,validation_dataset
    def train_validation_pca_split(self,X,y,train_rate=0.7,is_shuffle=True):
        data=[]
        for i in range(len(X)):
            data.append((X[i], y[i]))
        if is_shuffle:
            random.shuffle(data)
        split_index = int(len(data) * train_rate)
        train_data = data[:split_index]
        val_data = data[split_index:]
        X_train = []
        y_train = []
        for item in train_data:
            X_train.append(item[0])
            y_train.append(item[1])
        X_val = []
        y_val = []
        for item in val_data:
            X_val.append(item[0])
            y_val.append(item[1])

        # Listeyi NumPy dizisine çevir
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        X_val = np.array(X_val)
        y_val = np.array(y_val)
        return X_train,X_val,y_train,y_val
    def get_true_ones(self,dataset):
        return [i[-1] for i in dataset]
    def svm_transformation(self,array):
        return np.where(array == 0, -1, 1).astype(int)
    def type_function(self,array,array2):
        return np.array(array).astype(np.float32),np.array(array2).astype(int)
