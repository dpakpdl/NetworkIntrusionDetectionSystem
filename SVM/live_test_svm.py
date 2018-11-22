#!/usr/bin/python
"""list of libraries and functions imported"""
from numpy import *
import numpy as np
from sklearn.externals import joblib
from pca import principal_component_analysis
import os
import sys
from scapy.all import sniff

# attributes in our dataset CSIC 2010
attributes = ["Host", "Content-Length", "Content-Type", "Method"]
features = {'typ': ["Content-Type"], 'host': ["Host"], 'methods': ["Method"]}

# usual kinds of request and their numbering in order
methods = ["GET", "POST", "DELETE", "HEAD", "PUT", "TRACE", "CONNECT"]

# usual kinds of Content-Type and their numbering in order
typ = [" application/x-www-form-urlencoded", " application/json", " multipart/form-data", " application/ocsp-request",
       " text/plain;charset=UTF-8"]

# usual type of host
host = [" localhost:8080", " localhost:9090", " localhost:8090", " onlineparikshya.com", " localhost"]

# store key value pair of HTTP payload
dictionary = {}


# child function to write to a pipe
def child(pipeout):
    def search(search_key):
        for k in features:
            for v in features[k]:
                if search_key in v:
                    return k
        return None

    def is_http(packet):
        packet = str(packet)
        return "HTTP" in packet and any(method in packet for method in methods)

    def filter_packets(load):
        # filters the payload on basis of only the attributes required to us
        lv = load.split('\r\n')
        for i in lv:
            p = i.find(':')
            if p != -1:
                key = i[:p]
                value = i[p + 1:]
                # provide numerical value to content-type
                if key == 'Content-Type':
                    # eval converts string to preexisting variable name
                    try:
                        dictionary[key] = str(eval(search(key)).index(value) + 1)
                    except ValueError as ex:
                        dictionary[key] = str(int(math.log10(len(value))))
                        pass
                elif key == 'Host':
                    try:
                        dictionary[key] = str(eval(search(key)).index(value) + 1)
                    except ValueError as ex:
                        dictionary[key] = str(int(math.log10(len(value))))
                        pass
                elif key in attributes:
                    dictionary[key] = str(value)
                # assign default value
                for k in attributes:
                    if k not in dictionary:
                        dictionary[k] = str('10000')
                # calculation of Payload
                if dictionary['Method'] == '0':
                    try:
                        start = load.index('?')
                        end = load.index('HTTP/')
                        dictionary['Payload'] = str(len(load[start:end - 2]))
                    except ValueError:
                        return ""
                else:
                    dictionary['Payload'] = dictionary['Content-Length']

        feature_keys = ['Host', 'Payload', 'Content-Type', 'Content-Length', 'Method']
        values = [dictionary.get(feature) for feature in feature_keys]
        os.write(pipeout, str(values) + 'a')

    def start_sniff(packet):
        if is_http(packet):
            for att in methods:
                if att in str(packet):
                    dictionary['Method'] = str(methods.index(att) + 1)
            filter_packets(packet.load)

    sniff(prn=start_sniff)


def parent():
    """parent function to read from the pipe"""
    try:
        pipein, pipeout = os.pipe()
        if os.fork() == 0:
            child(pipeout)
        else:
            data = np.asarray([])
            while True:
                verse = os.read(pipein, 500)
                verse1 = verse.split('a')
                res = []
                for myList in verse1:
                    if myList != '':
                        data1 = eval(myList)
                        k = list(map(int, data1))
                        res.append(k)
                if len(res) > 1:
                    data_new = np.asarray(res)
                else:
                    data_new = np.asarray([[1, 237, 1, 237, 1]] + res)
                if all(data==data_new):
                    continue
                data = data_new
                live_data = mat(log10(data[:, :5]))
                try:
                    features_live = principal_component_analysis(live_data, 2)
                except:
                    continue

                classifier = joblib.load('trained_data/clf.pkl')
                prediction = classifier.predict(features_live)
                result = list()
                for i in prediction:
                    result.append(i)
                anomalous = True if 1 in result else False
                if anomalous:
                    print '---------> ANOMALOUS'
                else:
                    print '----------> NORMAL'
    except:
        os._exit(0)
        sys.exit(0)


if __name__ == '__main__':
    parent()
