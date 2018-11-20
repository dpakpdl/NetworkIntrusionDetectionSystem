#!/bin/python2.7
k = input("Enter value of K: ")
n = input("Enter n part for test set(quadrant) : ")

# original datasets
datasets=("normalcombinedWords.txt","anomalousTrafficTestWords.txt")

# f is original dataset iterator
for f in datasets:
    with open (f,"r") as _set:
        # read content of dataset
        data = _set.read()

        # ouput file names
        test = open("testing/test_"+f,"w")
        train =open("training/train_"+f,"w")

        # count number of payloads
        newlines = data.count('\n')

        # no. of parts resulted from k folds
        parts = newlines/(2**k)

        # no. of parts and lines counter
        part_count = 1
        line_count = 0

        # list of payload from dataset
        sentence=data.split('\n')

        # stores (temporarily) single fold
        lines = []

        # payload iterator in dataset
        for line in sentence:
            line_count=line_count+1
            lines.append(line)

            # if reached end of a fold
            if line_count%parts==0:
                # check of it should the test fold
                if part_count==n:
                    # append to test dataset
                    print >> test,  "\n".join(line for line in lines),""
                else :
                    # if is not test fold, append to training fold
                    print >> train, "\n".join(line for line in lines),""

                # clear to start new fold storage
                lines=[]
                # increase count of fold
                part_count=part_count+1

        test.close()
        train.close()
        trainNormal=open("training/train_normalcombinedWords.txt")
        trainAnomalous=open("training/train_anomalousTrafficTestWords.txt")
        testNormal=open("testing/test_normalcombinedWords.txt")
        testAnomalous =open("testing/test_anomalousTrafficTestWords.txt")

print "train Normal: ",len(trainNormal.read().split())
trainNormal.close()
print "test normal: ",len(testNormal.read().split())
testNormal.close()
print "train anomalous: ",len(trainAnomalous.read().split())
trainAnomalous.close()
print "test anomalous: ",len(testAnomalous.read().split())
testAnomalous.close()


