#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk	
import tags
import qna_parser
import sys
import math
from nltk.corpus import wordnet

class AutoFAQ:
    _quesList=[]
    _ansList=[]
    _quesListProcessed=[]
    _porter = nltk.PorterStemmer()
    _wnl = nltk.WordNetLemmatizer()
    WEIGHT_DICTIONARY=0.6
    WEIGHT_STEMMED=0.8
    #Threshold for finding closest question
    THRESHOLD=1
    CLOSENESS_THRESHOLD=0.1
    CLOSENESS_RATIO=0.1

    def  __init__(self):
        print("Welcome to AutoFAQ. Initializing AutoFAQ for you ...")
        
        #Parse the xml
        (self._quesList,self._ansList)=qna_parser.parse_file("input.xml")
        self._quesList=map(lambda ques:ques.lower(), self._quesList)
        self._ansList=map(lambda ques:ques.lower(), self._ansList)
        self._quesListProcessed = map(lambda q:tags.give_relevant_words(q), self._quesList)

    #Score b/w l1 and l2 list of words
    def score(self,l1,l2):
        score1=len(set(l1).intersection(l2))

        '''
        l1_stemmed=map(lambda a:self._porter.stem(a),l1)
        l2_stemmed=map(lambda a:self._porter.stem(a),l2)
        score2=set(l1_stemmed).intersection(l2_stemmed)*self.WEIGHT_STEMMED
        '''

        l1_stemmed=map(lambda a:self._wnl.lemmatize(a),l1)
        l2_stemmed=map(lambda a:self._wnl.lemmatize(a),l2)
        score2=len(set(l1_stemmed).intersection(l2_stemmed))*self.WEIGHT_STEMMED

        #Take into account all synonyms and all (eg. for What?)
        l1_with_dictionary=reduce(lambda x,y:x+y, map(lambda word:[l.name for s in wordnet.synsets(word) for l in s.lemmas],l1))
        l2_with_dictionary=reduce(lambda x,y:x+y, map(lambda word:[l.name for s in wordnet.synsets(word) for l in s.lemmas],l2))
        score3=len(set(l1_with_dictionary).intersection(l2_with_dictionary))*self.WEIGHT_DICTIONARY

        return float(score1+score2+score3)/math.sqrt(len(l2)*len(l1))

    #Returns the index of the closest_match with the score of it
    def closest_question(self,queryWords):
        scoreList=map(lambda ques: self.score(queryWords, ques), self._quesListProcessed)
        maxScore=max(scoreList)
        if (len(filter(lambda x: x>= maxScore-self.CLOSENESS_THRESHOLD, scoreList)) < len(self._quesList)*self.CLOSENESS_RATIO ):
            return (scoreList.index(maxScore),maxScore)
        else:
            print "Hi"
            #Raise error - TOO MANY CLOSE QUESTIONS
            return 1

    def answer_from(self, queryWords, qIndex):
        #Answer queryWords from ansList[qIndex]
        return self._ansList[qIndex]
    
    def respond(self,query):
        response=""
        queryWords=tags.give_relevant_words(query)
        #print queryWords

        (qIndex,qConf)=self.closest_question(queryWords)
        
        if qConf>self.THRESHOLD:
            print self.answer_from(queryWords, qIndex)

        print "Index :",qIndex
        print "Question closest to your query is :",self._quesList[qIndex],qConf

        # Find the closest match to the answer
        try:
            (qIndex,qConf)=self.closest_question(queryWords)
        
            if qConf>self.THRESHOLD:
               print self.answer_from(queryWords,qIndex)

            print "Index :",qIndex
            print "Question closest to your query is :",self._quesList[qIndex],qConf

        except:
            newQuery=raw_input("Cannot identify a good source to answer your question.\nCan you please add some more information?\n")
            self.respond(query+newQuery)

if __name__ == "__main__":
    autofaq=AutoFAQ()

    query=raw_input("Please enter your Query\n");
    query.lower()

    autofaq.respond(query)