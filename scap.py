#!/bin/python2.7

from scapy.all import *
from random import randint
# attributes in our dataset CSIC 2010
attributes= ["Host","Content-Length","Content-Type"]
features= {'typ':["Content-Type"],'host':["Host"]}

# usual kinds of request and their numbering in order
methods= ["GET","POST","DELETE","HEAD","PUT","TRACE","CONNECT"]

#usual kinds of Content-Type and their numbering in order
typ=[" application/x-www-form-urlencoded"," application/json"," multipart/form-data", " application/ocsp-request",
" text/plain;charset=UTF-8", " application/ipp", " application/javascript; charset=utf-8", " text/html", " application/pdf"]

#usual type of host
host=[]

#store key value pair of HTTP payload
dictionary = {}

#file to store data offline
f = open('http_live.txt', 'w')

#return index KEY for words in dictionary
def search(searchFor):
    for k in features:
        for v in features[k]:
            if searchFor in v:
                return k
    return None

def isHttp(packet):
    packet = str(packet)
    return "HTTP" in packet and any(i in packet for i in methods)

# filters the payload on basis of only the attributes required to us
def filter(load):
    lv = load.split('\r\n')
    for i in lv:
        p = i.find(':')
        if p != -1:
            key = i[:p]
            value = i[p+1:]
            #provide numerical value to content-type
            if key =='Content-Type':
                #EVAL CONverts string to preexisting variable name
                dictionary[key]=str(eval(search(key)).index(value)+1)
            elif key == 'Host':
            	dictionary[key]= str(randint(0,9))
            elif key in attributes: dictionary[key]=str(value)
            #assign default value
            for k in attributes:
                if k not in dictionary:
                    dictionary[k]=str('0')
           # calculation of Payload
            if dictionary['Method']=='0':
                try:
                    start=load.index('?')
                    end=load.index('HTTP/')
                    dictionary['Payload']=str(len(load[start:end-2]))
                except ValueError:
                    return ""
            else:
                dictionary['Payload']=dictionary['Content-Length']
	#print dictionary.values()
    # writing data in file
    for k,v in dictionary.items():
        f.flush()
        print k+': '+v+"\n",
        print >> f,k+': '+v,
    print >> f
    print
    dictionary.clear()

def pfunc(packet):
    if isHttp(packet):
        for att in methods:
            if att in str(packet):
                dictionary['Method'] = str(methods.index(att))
        load = packet.load
        filter(packet.load)

data = sniff(prn=pfunc)
print data
