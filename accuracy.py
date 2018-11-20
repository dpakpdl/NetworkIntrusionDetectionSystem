#!/bin/python2.7
from __future__ import division
from sklearn.externals import joblib
from nltk.probability import FreqDist
from nltk import classify
from nltk.classify.naivebayes import NaiveBayesClassifier

#load the models
classifier = joblib.load('models/classifier_compressed.pkl')
word_features = joblib.load('models/word_features_compressed.pkl')

"""
    checks if the passed list of words
    is contained in the list 'word_features'
    true if yes
    false if no
"""
def extract_features(document):
    document_words = set(document)
    features = {}
    global word_features	
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features
    print e

"""
    Reading files in chucks of 1KB each
"""
def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

# parameters for accuracy
TP=FN=TN=FP=0

#open files for normal
try:
    normal_test_classified = open('test_classified/Our_Normal_test_classified.txt','w')
    nor = open('datasets/testing/test_normalcombinedWords.txt')
except Exception as e:
    print e

#classify normal test dataset
for piece in read_in_chunks(nor):
    piece=piece.lower()
    lines=piece.split('\n')
    for line in lines:
        classed=classifier.classify(extract_features(line.split()))
        if classed=='normal':
            TP=TP+1
        else :
            FN=FN+1
        print >> normal_test_classified,line,"--->",classed
normal_test_classified.close()
nor.close()
print "TP: %d"%TP
print "FN: %d"%FN

#open files for Anomalous
try:
    ano = open('datasets/testing/test_anomalousTrafficTestWords.txt')
    ano_test_classified = open('test_classified/Our_Anomalous_test_classified.txt','w')
except Exception as e:
    print e

#classify anomalous tets datasets
for piece in read_in_chunks(ano):
    piece=piece.lower()
    lines=piece.split('\n')
    for line in lines:
        classed=classifier.classify(extract_features(line.split()))
        if classed=='anomalous':
            TN=TN+1
        else :
            FP=FP+1
	print >> ano_test_classified,line,"--->",classed
ano.close()
ano_test_classified.close()
a=open('test_classified/accuracy.txt','w')

print "TN: %d"%TN
print "FP: %d"%FP
print "Accuracy: %.3f "%((TP+TN)/(TP+TN+FP+FN))
print "Sensitivity: %.3f "%((TP)/(TP+FN))
print "Specificity: %.3f "%((TN)/(TN+FP))
print "Precision: %.3f "%((TP)/(TP+FP))

print >>a, "TN: %d"%TN
print >>a, "FP: %d"%FP
print >>a, "Accuracy: %.3f "%((TP+TN)/(TP+TN+FP+FN))
print >>a, "Sensitivity: %.3f "%((TP)/(TP+FN))
print >>a, "Specificity: %.3f "%((TN)/(TN+FP))
print >>a, "Precision: %.3f "%((TP)/(TP+FP))
