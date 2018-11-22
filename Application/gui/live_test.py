#!/bin/python2.7
from scapy.all import *
import re
import time
import urllib
from sklearn.externals import joblib

# load the models
classifier = joblib.load('models/classifier_compressed.pkl')
word_features = joblib.load('models/word_features_compressed.pkl')

# usual kinds of request and their numbering in order
METHODS = ["GET", "POST", "DELETE", "HEAD", "PUT", "TRACE", "CONNECT"]

# store key value pair of HTTP payload
OBTAINED_PAYLOAD = {}


def extract_features(document):
    """
    checks if the passed list of words is contained in the list 'word_features'
    """
    document_words = set(document)
    features = {}
    global word_features
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features


def find_user_agent(load, value, n=3):
    """
    find string between user-agent and third raw string raw newline
    """
    start = load.find(value)
    while start >= 0 and n > 1:
        start = load.find(value, start + 1)
        n -= 1
    return start


def is_http(packet_captured):
    """check if a packet is valid http request"""
    packet_captured = str(packet_captured)
    return "HTTP" in packet_captured and any(method in packet_captured for method in METHODS)


def parse_request(s, c, n):
    """parses http payload using regex"""
    regex = r'^((?:[^%s]*%s){%d}[^%s]*)%s(.*)' % (c, c, n - 1, c, c)
    l = ()
    m = re.match(regex, s)
    if m: l = m.group(2)
    return l


def classify_live_data(load, mac_src, ip_src, add_line):
    """classifies the live http header payloads"""
    global input_file
    input_file.flush()
    global STOP_EV
    # finding User-Agent
    try:
        srt = load.index('User-Agent:')
    except ValueError:
        srt = 0
    if srt:
        finish = find_user_agent(load, "\r\n")
        # finding URL
        try:
            start = load.index(' ')
        except ValueError:
            start = 0
        if start:
            end = load.index('HTTP')

            # Regular expression to substitute unwanted characters from http load
            p = re.compile('\+|\=|\&')
            # if it is a get request
            if OBTAINED_PAYLOAD['Method'] == '0':
                # take the header title payload
                try:
                    # classify the load after removing & + = etc and substitute them by space
                    classed = classifier.classify(
                        extract_features(str(p.sub(' ', load[start + 1:end])).lower().split()))
                    print >> input_file, mac_src + "\n" + ip_src + "\n" + str(load[srt:finish])
                    print >> input_file, urllib.unquote(str(load[start + 1:end])) + "\n" + classed
                    # print mac_src + "\n"+ ip_src + "\n" + str(load[srt:finish])+ "\n" +
                    # urllib.unquote(str(load[start+1:end]))+ "\n"+ classed
                    # write source ip address, User-agent and Payload with class respectively to log
                    if not STOP_EV.is_set():
                        if add_line:
                            add_line(mac_src)
                            add_line(ip_src)
                            add_line(str(load[srt:finish]))
                            add_line(urllib.unquote(str(load[start + 1:end])))
                            add_line(str(classed))
                except ValueError:
                    return ""

            elif OBTAINED_PAYLOAD['Method'] != '0':
                # get to the last line of packet
                reg = load[start + 1:end] + parse_request(load, '\r\n', load.count('\r\n'))
                # classify the load after removing & + = etc and substitute them by space
                classed = classifier.classify(extract_features(p.sub(' ', str(reg).lower()).split()))
                print >> input_file, mac_src + "\n" + ip_src + "\n" + str(load[srt:finish])
                print >> input_file, urllib.unquote(str(reg)) + "\n" + classed
                # print mac_src + "\n" + ip_src + "\n" + str(load[srt:finish]) +
                #  "\n" + urllib.unquote(str(reg)) + "\n"+ classed
                # write source ip adress, User-agent and Payload with class respectively to log
                if not STOP_EV.is_set():
                    if add_line:
                        add_line(mac_src)
                        add_line(ip_src)
                        add_line(str(load[srt:finish]))
                        add_line(urllib.unquote(str(reg)))
                        add_line(str(classed))
        else:
            pass
    else:
        pass


def sniff_packets(packet_captured):
    """pass the request of it valid http header"""
    global GUI
    if is_http(packet_captured) and IP in packet_captured:
        ip_src = packet_captured[IP].src
        for method in METHODS:
            if method in str(packet_captured):
                OBTAINED_PAYLOAD['Method'] = str(METHODS.index(method))
                classify_live_data(packet_captured.load, packet_captured.src, ip_src, GUI)


GUI = None
STOP_EV = None

# file to store data offline(logs)
moment = time.strftime("%Y-%m-%d__%H_%M_%S", time.localtime())
input_file = open('logs/log-' + moment + '.txt', 'w')


def start_sniff(thegui, stopev):
    global GUI
    global STOP_EV
    STOP_EV = stopev
    GUI = thegui
    # sniffer
    sniff(prn=sniff_packets)


if __name__ == "__main__":
    start_sniff(None, None)
