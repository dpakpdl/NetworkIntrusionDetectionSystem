
#!/bin/python2.7
from scapy.all import *
import re

#file to store words
f = open('../../Dataset/Datasets-after-feature-extraction/Naives-Bayes/normalCombinedWords.txt', 'w')


def checkForMethod(load):
    """
    check data if data is in packet body or title
    return 0 if in body i.e. it is not a standard  packet
    """
    regex=re.compile(r'^GET|^POST|^HEAD|^PUT|^TRACE|^CONNECT',re.M)
    m=regex.search(load)
    if m:
        return 1
    else:
        return 0

def checkForGet(load):
    # Check if its a valid GET request
    regex=re.compile(r'GET',re.M)
    if (regex.search(load)):
        return 1
    return 0


def filter(load):
    # filters the payload on basis of only the attributes
    p=re.compile('\+|\&|\=')
    # extract attributes from header body
    if (checkForMethod(load)==0):
        print >> f, str(p.sub(' ',load))

    # extract attributes from GET request    
    if (checkForGet(load)):
           try:
               start=load.index('?')
               end=load.index(' HTTP/')
               print >> f,str(p.sub(' ',load[start+1:end]))
           except ValueError:
               return ""

def fromfile(filename):
    f = open(filename)
    fstr = f.read()
    strpackets = fstr.split('\r\n\r\n')
    for packet in strpackets:
        filter(packet)

fromfile("../../Dataset/Original-Datasets/normalCombined.txt")
