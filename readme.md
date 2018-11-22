# Network Intrusion Detection System

It is an web-based attack detection system using the CSIC 2010 HTTP datatsets. We used features extraction and reduction techniques to reduce dimension of the Dataset. We used two techniques to build the attack detection model. 1) SVM model  2) Probabalistic Model Using Naives Bayes

## Repository Folder Structure
* Dataset:  Contains the original datasets and the sample datasets after features extraction for the SVM and Bayes Models.
	k-fold.py Used to extract part of datatsets separately for training and testing.
* Features Extract: Contains the code used to extract features for the SVM and Bayes Models.
* Application
	1) accuracy.py  Used to find the measures such as accuracy, sensitivity, specificity, precision, etc.
	2) live_test.py Used to classify online packets using Bayes Model.
	3) model_classfier.py Used to build models from datasets for Bayes model after using k-fold.py
	4) test_classifer.py Used to test models offline.

* gui: It is basically  live_test.py running using graphical interface.
* SVM: Contains files for the SVM approach. 

## Requirements
1) Python 2
2) Numpy
3) Scipy
4) Scikit-Learn 
5) Nltk
6) Gtk

## Install

This application can be cloned from github repository and installed. Following the procedure given below:

* git clone `https://github.com/dpakpdl/NetworkIntrusionDetectionSystem.git`

## Run

The app can be run with the command below:

* cd Application/gui
* pip install scapy
* pip install -U scikit-learn
* pip install -U nltk
* sudo python nids.py 

## Framework

The application is written in python 2.
