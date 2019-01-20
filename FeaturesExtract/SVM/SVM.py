import json
import numpy as np
from numpy import *
import os
from sklearn.model_selection import train_test_split, KFold
from sklearn import svm, metrics


class DimensionalityMissMatchException(Exception):
    pass


class DataSetManager(object):
    def __init__(self):
        self.normal = None
        self.anomalous = None
        self.merged_data = None

    def load_data_sets(self):
        # self.normal = loadtxt('/home/deepak/Major/nrmlTffTrngMdfd.txt', delimiter=' ', skiprows=1)
        # self.anomalous = loadtxt('/home/deepak/Major/SVM/anomalousTrafficTestModified.txt', delimiter=' ', skiprows=1)
        self.normal = loadtxt('//NetworkIntrusionDetectionSystem/SVM/Dataset/normal_data_new.csv', delimiter=',', skiprows=1)
        self.anomalous = loadtxt('/NetworkIntrusionDetectionSystem/SVM/Dataset/anomalous_data_new.csv', delimiter=',', skiprows=1)

    def add_labels(self):
        normal_samples, normal_features = shape(self.normal)
        normal_label = np.zeros((normal_samples, 1))
        self.normal = np.append(self.normal, normal_label, axis=1)
        anomalous_samples, anomalous_features = shape(self.anomalous)
        anomalous_label = np.ones((anomalous_samples, 1))
        self.anomalous = np.append(self.anomalous, anomalous_label, axis=1)

    def merge_data_sets(self):
        _, normal_features = shape(self.normal)
        _, anomalous_features = shape(self.anomalous)
        if normal_features != anomalous_features:
            raise DimensionalityMissMatchException('Number of features in normal and anomalous data missmatch')
        self.merged_data = np.concatenate((self.normal, self.anomalous), axis=0)
        np.random.shuffle(self.merged_data)
        _, merged_features = shape(self.merged_data)
        if normal_features != merged_features:
            raise DimensionalityMissMatchException('Number of features in normal and merged data missmatch')


class MySVM(object):
    def __init__(self, data_set, kfolds=2):
        self.data_set = data_set
        self.targets = None
        self.kfolds = kfolds
        self.targets = data_set[:, 5]
        self.result_file_path = ''

    def split_data_set(self):
        self.targets = self.data_set[:, 5]
        x_train, x_test, y_train, y_test = train_test_split(self.data_set, self.targets, test_size=.3)
        print('Training data and target sizes: \n{}, {}'.format(x_train.shape, y_train.shape))
        print('Test data and target sizes: \n{}, {}'.format(x_test.shape, y_test.shape))
        return x_train, x_test, y_train, y_test

    def cross_validate_split(self):
        k_folds = KFold(n_splits=self.kfolds)
        count = 0
        for train_index, test_index in k_folds.split(self.data_set):
            count += 1
            self.classify(self.data_set[train_index], self.data_set[test_index], self.targets[train_index], self.targets[test_index], count=count)

    def classify(self, x_train, x_test, y_train, y_test, count):
        classifier = svm.SVC(gamma=0.001, C=10)
        classifier.fit(x_train, y_train)
        y_pred = classifier.predict(x_test)
        target_names = ['Normal', 'Anomalous']
        print("-------------------------------------------------------------------------------")
        print("Classification report for classifier %s:\n%s\n"
              % (classifier, metrics.classification_report(y_true=y_test, y_pred=y_pred, target_names=target_names)))
        conf_matrix = metrics.confusion_matrix(y_test, y_pred)
        # conf_matrix = np.array([[8616, 299], [0, 0]])
        print("Confusion matrix:\n%s" % conf_matrix)
        train_count, _ = shape(x_train)
        test_count, _ = shape(x_test)

        self.write_to_json(self.calculate_metrics(conf_matrix, count, train_count, test_count))

    def calculate_metrics(self, conf_matrix, count, train_count, test_count):
        TP = float(conf_matrix[0][0])
        FP = float(conf_matrix[0][1])
        FN = float(conf_matrix[1][0])
        TN = float(conf_matrix[1][1])
        accuracy = ((TP + TN) / (TP + TN + FP + FN))
        sensitivity = (TP / (TP + FN))
        specificity = (TN / (TN + FP))
        precision = (TP / (TP + FP))
        print "Accuracy: %.3f " % accuracy
        print "Sensitivity: %.3f " % sensitivity
        print "Specificity: %.3f " % specificity
        print "Precision: %.3f " % precision
        kfold = self.kfolds
        dict_key = str(kfold) + '.' + str(count)
        result = dict(accuracy=accuracy, sensitivity=sensitivity, specificity=specificity, precision=precision, training_data=train_count, testing_data=test_count)
        return {dict_key: result}

    def write_to_json(self, result):
        content = dict()
        if os.path.exists(self.result_file_path):
            with open(self.result_file_path, 'r') as infile:
                content = json.load(infile) if infile else {}
        if content.get(str(self.kfolds)):
            k_content = content.get(str(self.kfolds))
            k_content.update(result)
        else:
            content.update({
                self.kfolds: result
            })
        with open(self.result_file_path, 'w') as outfile:
            json.dump(content, outfile)

    def set_result_file_path(self, filepath):
        self.result_file_path = filepath

    def normal_classify(self):
        x_train, x_test, y_train, y_test = self.split_data_set()
        classifier = svm.SVC(gamma=0.001)
        classifier.fit(x_train, y_train)
        y_pred = classifier.predict(x_test)
        print("Classification report for classifier %s:\n%s\n"
              % (classifier, metrics.classification_report(y_test, y_pred)))
        print("Confusion matrix:\n%s" % metrics.confusion_matrix(y_test, y_pred))

if __name__ == "__main__":
    data_manager = DataSetManager()
    data_manager.load_data_sets()
    data_manager.add_labels()
    data_manager.merge_data_sets()
    mysvm = MySVM(data_manager.merged_data, kfolds=4)
    mysvm.set_result_file_path('/NetworkIntrusionDetectionSystem/SVM/Results/result.json')
    mysvm.cross_validate_split()
