from sklearn.externals import joblib
from nltk import classify
from nltk.classify.naivebayes import NaiveBayesClassifier

classifier = joblib.load('models/classifier_compressed.pkl')
word_features = joblib.load('models/word_features_compressed.pkl')


def extract_features(document):
    """
        checks if the passed list of words
        is contained in the list 'word_features'
    """
    document_words = set(document)
    features = {}
    global word_features	
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

print classifier.show_most_informative_features()
#print classifier

test_word='Select modo from registrar'
print classifier.classify(extract_features(test_word.lower().split()))
