from nltk.probability import FreqDist
from sklearn.externals import joblib
from nltk import classify
from nltk.classify.naivebayes import NaiveBayesClassifier

# open training dataset files
try:
    ano = open('../Dataset/Datasets-after-feature-extraction/Naives-Bayes/training/train_anomalousTrafficTestWords.txt')
    nor = open('../Dataset/Datasets-after-feature-extraction/Naives-Bayes/training/train_normalcombinedWords.txt')
except Exception as e:
    print e


def read_in_chunks(file_object, chunk_size=1024):
"""
    Reading files in chucks of 1KB each
"""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

"""
    constains the training data
    is a list containing tuple of list and label
    list is set of words from each sentence
    label is class of sentence
"""
training=[]

"""
    make single training sets
    provide label to each http header payload
    as anomalous or normal
"""
for piece in read_in_chunks(ano):
    lines=piece.split('\n')
    for words in lines:
        words_separated=[e.lower() for e in words.split()]
        training.append((words_separated,'anomalous'))

for piece in read_in_chunks(nor):
    lines=piece.split('\n')
    for words in lines:
        words_separated=[e.lower() for e in words.split()]
        training.append((words_separated,'normal'))

"""
    third argument is used for compression 
    0-9, higher number gives more compression
    but processing is slow
    3 is a good compromise
"""
#print training
joblib.dump(training,'models/training_compressed.pkl',3)

def get_words_in_tweets(training):
"""
    makes single list of words from training
    single list of all the http header payload
"""
    all_words = []
    for (words, sentiment) in training:
      all_words.extend(words)
    #print all_words
    return all_words

def get_word_features(wordlist):
"""
    gives the frequency count of
    each word from the dataset
    But, here we return only the keys
    i.e. only the word non-repeating words
"""
    wordlist = FreqDist(wordlist)
    #print wordlist.keys(),"------->",wordlist.values()
    return wordlist.keys()

#word_features = get_words_in_tweets(training)
training=joblib.load('models/training_compressed.pkl')
word_features = get_word_features(get_words_in_tweets(training))
joblib.dump(word_features,'models/word_features_compressed.pkl',3)
#print word_features

training=joblib.load('models/training_compressed.pkl')
word_features=joblib.load('models/word_features_compressed.pkl')


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

#print extract_features(training[0][0])

training_set = classify.apply_features(extract_features, training)
#print training_set
classifier = NaiveBayesClassifier.train(training_set)
joblib.dump(classifier, 'models/classifier_compressed.pkl',3)
