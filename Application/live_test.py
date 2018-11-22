#!/bin/python2.7
from scapy.all import *
import re
import time
import urllib
from sklearn.externals import joblib
from nltk.probability import FreqDist
from nltk import classify
from nltk.classify.naivebayes import NaiveBayesClassifier

#load the models
classifier = joblib.load('models/classifier_compressed.pkl')
word_features = joblib.load('models/word_features_compressed.pkl')


def extract_features(document):
    """
        checks if the passed list of words
        is contained in the list 'word_features'
        true if yes
        false if no
    """
    document_words = set(document)
    features = {}
    global word_features	
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


def find_Useragent(load,value,n=3):
    """
        find string between User-agent and third raw string raw newline
    """
    start = load.find(value)
    while start >= 0 and n > 1:
        start = load.find(value, start+1)
        n -= 1
    return start

def isHttp(packet):
    #check if it a valid http request
    packet = str(packet)
    return "HTTP" in packet and any(i in packet for i in methods)

def nthofchar(s, c, n):
    # use of regular expression to break http load
    regex=r'^((?:[^%s]*%s){%d}[^%s]*)%s(.*)' % (c,c,n-1,c,c)
    l = ()
    m = re.match(regex, s)
    if m: l = m.group(2)
    return l

# usual kinds of request and their numbering in order
methods= ["GET","POST","DELETE","HEAD","PUT","TRACE","CONNECT"]

#store key value pair of HTTP payload 
dictionary = {}

#file to store data offline(logs)
moment=time.strftime("%Y-%b-%d__%H_%M_%S",time.localtime())
f = open('logs/log-'+moment+'.txt', 'w')

def classify(load,mac_src,ip_src):
    """
    Classify the live http header payloads
    finding User-Agent
    """
    try:
        srt=load.index('User-Agent:')
    except ValueError:
        srt = 0
    if srt:
        finish= find_Useragent(load,"\r\n")
        #finding URL
        start=load.index(' ')
        if start:
            end=load.index('HTTP')
            
            # Regular expresssion to substitute unwanted characters from http loadjjj
            p=re.compile('\+|\=|\&')
            #if it is a get request
            if dictionary['Method']=='0':
                # take the header title payload
                try:
                    # classify the load after removing & + = etc and substitute them by space
                    classed=classifier.classify(extract_features(str(p.sub(' ',load[start+1:end])).lower().split()))
                    print mac_src + "\n"+ ip_src + "\n" + str(load[srt:finish])+ "\n" + urllib.unquote(str(load[start+1:end]))+ "\n"+ classed
                    # write source ip adress, User-agent and Payload with class respectively to log
                    print >>f,mac_src + "\n" + ip_src + "\n" + str(load[srt:finish])
                    print >>f,urllib.unquote(str(load[start+1:end])) + "\n" + classed
                except ValueError:
                    return ""
	
            elif dictionary['Method']!='0':
                #get to the last line of packet
                reg= load[start+1:end]+nthofchar(load,'\r\n',load.count('\r\n'))
                # classify the load after removing & + = etc and substitute them by space
                classed=classifier.classify(extract_features(p.sub(' ',str(reg).lower()).split()))
                print mac_src + "\n" + ip_src + "\n" + str(load[srt:finish]) + "\n" + urllib.unquote(str(reg)) + "\n"+ classed 
                # write source ip adress, User-agent and Payload with class respectively to log
                print >>f,mac_src + "\n" + ip_src + "\n" + str(load[srt:finish])
                print >>f,urllib.unquote(str(reg)) + "\n" + classed
	else:
            pass
	
def pfunc(packet):
    #pass the request of it valid http header
    if isHttp(packet):
        if IP in packet:
            ip_src=packet[IP].src
            for att in methods:
                if att in str(packet):
                    dictionary['Method'] = str(methods.index(att)) 
                    classify(packet.load,packet.src,ip_src)

#sniffer
sniff(prn=pfunc)
