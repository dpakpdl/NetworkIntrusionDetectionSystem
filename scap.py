#!/bin/python2.7

from scapy.all import *
from random import randint

# attributes in our dataset CSIC 2010
ATTRIBUTES = ["Host", "Content-Length", "Content-Type"]
FEATURES = {'typ': ["Content-Type"], 'host': ["Host"]}

# usual kinds of request and their numbering in order
METHODS = ["GET", "POST", "DELETE", "HEAD", "PUT", "TRACE", "CONNECT"]

# usual kinds of Content-Type and their numbering in order
CONTENT_TYPE = [" application/x-www-form-urlencoded", " application/json", " multipart/form-data",
                " application/ocsp-request",
                " text/plain;charset=UTF-8", " application/ipp", " application/javascript; charset=utf-8", " text/html",
                " application/pdf"]

# usual type of host
HOST = []

# store key value pair of HTTP payload
OBTAINED_PAYLOAD = {}

# file to store data offline
input_file = open('http_live.txt', 'w')


# return index KEY for words in dictionary
def search(search_key):
    for key, value in FEATURES:
        if search_key in value:
            return key
    return None


def is_http(packet_captured):
    packet_captured = str(packet_captured)
    return "HTTP" in packet_captured and any(method in packet_captured for method in METHODS)


# filters the payload on basis of only the attributes required to us
def filter_payload(load):
    lv = load.split('\r\n')
    for i in lv:
        p = i.find(':')
        if p != -1:
            key = i[:p]
            value = i[p + 1:]
            # provide numerical value to content-type
            if key == 'Content-Type':
                # EVAL CONverts string to preexisting variable name
                OBTAINED_PAYLOAD[key] = str(eval(search(key)).index(value) + 1)
            elif key == 'Host':
                OBTAINED_PAYLOAD[key] = str(randint(0, 9))
            elif key in ATTRIBUTES:
                OBTAINED_PAYLOAD[key] = str(value)
            # assign default value
            for k in ATTRIBUTES:
                if k not in OBTAINED_PAYLOAD:
                    OBTAINED_PAYLOAD[k] = str('0')
                    # calculation of Payload
            if OBTAINED_PAYLOAD['Method'] == '0':
                try:
                    start = load.index('?')
                    end = load.index('HTTP/')
                    OBTAINED_PAYLOAD['Payload'] = str(len(load[start:end - 2]))
                except ValueError:
                    return ""
            else:
                OBTAINED_PAYLOAD['Payload'] = OBTAINED_PAYLOAD['Content-Length']
                # print dictionary.values()
    # writing data in file
    for k, v in OBTAINED_PAYLOAD.items():
        input_file.flush()
        print k + ': ' + v + "\n",
        print >> input_file, k + ': ' + v,
    print >> input_file
    print
    OBTAINED_PAYLOAD.clear()


def sniff_packet(packet_captured):
    if is_http(packet_captured):
        for method in METHODS:
            if method in str(packet_captured):
                OBTAINED_PAYLOAD['Method'] = str(METHODS.index(method))
        filter_payload(packet_captured.load)


data = sniff(prn=sniff_packet)
print data
