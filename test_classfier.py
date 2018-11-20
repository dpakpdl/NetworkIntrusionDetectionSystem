from sklearn.externals import joblib
from nltk import classify
from nltk.classify.naivebayes import NaiveBayesClassifier

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

#print classifier.show_most_informative_features()
#print classifier

mka='funes'
print classifier.classify(extract_features(mka.lower().split()))
