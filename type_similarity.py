#!/usr/bin/env python
# -*- coding: utf-8 -*-
#type_similarity.py

def get_matrix_english(fileName):
    f=open(fileName)
    ls=f.readlines()
    f.close()
    
    #Remove all the hashes
    ls=filter(lambda line: '#' not in line, ls)
    ls=map(lambda line: line.replace("\n",""), ls)
    ls=map(lambda line: line.split(";"), ls)
    
    #Assumption tags in first line
    matrix={}
    tags=ls[0]
    scores=ls[1:]

    for t in tags:
        matrix[t]={}

	length=len(tags)
    #Asser that the size of the scores is length as well
    if not (len(scores) == len(tags)):
        print "Length of the tags is",len(tags)
        print "Length of the scores is",len(scores)
        print "They should be equal"
        raise AssertionError

    for i in xrange(length):
        for j in xrange(length):
            if j>i:
                matrix[tags[i]][tags[j]]=scores[j][i]
            else:
                matrix[tags[i]][tags[j]]=scores[i][j]

    return matrix

if __name__ == "__main__":
    print get_matrix_english("ques_similarity_matrix.txt")
