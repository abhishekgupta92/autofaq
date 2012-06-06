#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk	
import tags
import qna_parser
import templateParser
import sys
import math
import xml.dom.minidom as minidom
from nltk.corpus import wordnet

class AutoFAQ:
    _quesList=[]
    _ansList=[]
    _quesListProcessed=[]
    _porter = nltk.PorterStemmer()
    _wnl = nltk.WordNetLemmatizer()
    _templates=[]
    _qtypes=[]
    WEIGHT_DICTIONARY=0.6
    WEIGHT_STEMMED=0.8
    #Threshold for finding closest question
    THRESHOLD=1
    CLOSENESS_THRESHOLD=0.1
    CLOSENESS_RATIO=0.1
    QUESTION_WORD_TAGS=['WP','WRB']
    SENTENCE_DIVIDERS=['']
    
    def  __init__(self):
        print("Welcome to AutoFAQ. Initializing AutoFAQ for you ...")
        
        #Parse the xml
        (self._quesList,self._ansList)=qna_parser.parse_xml("input.xml")
        self._quesList=map(lambda ques:ques.lower(), self._quesList)
        self._ansList=map(lambda ques:ques.lower(), self._ansList)
        self._quesListProcessed = map(lambda q:tags.give_relevant_words(q), self._quesList)

        #Parse the templates
        (self._templates,self._qtypes)=templateParser.parse_xml("templates.xml")
        print self._templates
        print self._qtypes

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

        print scoreList
        #Check if there are some questions to close to the highest scoring function in the scoreList
        if (len(filter(lambda x: x>= maxScore-self.CLOSENESS_THRESHOLD, scoreList)) < len(self._quesList)*self.CLOSENESS_RATIO ):
            return (scoreList.index(maxScore),maxScore)
        else:
            return (None,None)

    def answer_from(self, queryWords, qIndex):
        #Answer queryWords from ansList[qIndex]
        return self._ansList[qIndex]
    
    def match_type(self, toMatch, matchWith):
        matchName = matchWith.nodeName.encode()
        matchVal = matchWith.childNodes[0].nodeValue.encode()
        if matchName == 'word':
            if toMatch[0] == matchVal:
                return True
            else:
                return False
        elif matchName == 'tag':
            if toMatch[1] in matchVal:
                return True
            else:
                return False
        else:
            return False                                    
        
    def type(self, query):
        query=query.lower().split()
        query_tags=nltk.pos_tag(query)
        index = 0
        matchDone = False		
        for template in self._templates:
            if not(matchDone):
                tempTags = query_tags[:]
                parsedTemplate = minidom.parseString('<xml>'+template+'</xml>')
                exit = False
                for domNode in parsedTemplate.childNodes[0].childNodes:
                    if not(exit):
                        nodeName = domNode.nodeName.encode()
                        if nodeName != 'qmark' and nodeName != 'X':
                            textValNode = domNode.childNodes[0].nodeValue.encode()
                
                        if nodeName == 'word':
                            if textValNode == tempTags[0][0]:
                                tempTags.pop(0)
                            else:
                                index += 1
                                exit = True
                        elif nodeName == 'tag':
                            if tempTags[0][1] in textValNode:
                                tempTags.pop(0)
                            else:
                                index += 1
                                exit = True
                        elif nodeName == 'X':
                            brother = domNode.nextSibling
                            brotherName = brother.nodeName.encode()
                            if brotherName == 'qmark':
                                tempTags = tempTags[len(tempTags) - 1]
                            else:
                                brotherVal = brother.childNodes[0].nodeValue.encode()
                                tempIndex = 0
                                while not(self.match_type(tempTags[tempIndex], brother)):
                                    tempIndex += 1
                                
                                if tempIndex >= len(tempTags):
                                    # Exit the function because the query is not well formed. It's missing a question mark.
                                    return "".decode()
                                else:
                                    tempTags = tempTags[tempIndex:len(tempTags)]
                        else:
                            # This is the case when the tag is <qmark/>
                            if tempTags[0][0] == '?':
                                [tempTags].pop(0)
                                exit = True
                                matchDone = True
                            else:
                                print "Sorry your question doesn't seem to be well formed. It seems to be missing a question mark"
                                return "".decode()
        
        if index == len(self._qtypes):
            print "Sorry but your question does not match any question types"
            return "".decode()
        else:
            print "The type of your question is : ", self._qtypes[index].encode()
            return self._qtypes[index]                     

    def stringPos(self, toSearch, searchIn):
        index = 0
        while toSearch != searchIn[index][0]:
            index += 1
        return index
        
    def tagPos(self, searchIn, tagsList):
        index = 0
        while (index < len(searchIn) -1) and not(searchIn[index][1] in tagsList):
            index += 1
        return index            
        
    # Assumption that the answers in the FAQ files are of positive connotation,
    # like : "Delhi is capital of India" and not "Delhi is not the capital of USA".
    # I will work on removing this assumption soon.
    # @param qtype The Question Type in a Unicode String    
    def answer_construct(self, qtype, question, answer):
        ques_type = qtype.encode()
        asked = nltk.pos_tag(question.lower().split())
        reply = nltk.pos_tag(answer.lower().split())
        if ques_type == 'ynq':
            print asked
            print reply
            posIs = self.stringPos('is', asked)
            # Need to add other tags about which to break. Currently only DT is here.
            posBreakStart = self.tagPos(asked, 'DT')
            posOf = self.stringPos('of', asked)
            print posOf
            posBreakEnd = self.tagPos(asked, 'CC')
            print posBreakEnd
            ansChunkOne = asked[posIs+1:posBreakStart]
            ansChunkTwo = asked[posOf+1:posBreakEnd]
            posIs = self.stringPos('is', reply)
            # Currently using the starting position for the chunk to be the start of the sentence. Have to find some generic method.
            posOf = self.stringPos('of', reply)
            posBreakEnd = self.tagPos(reply, 'CC')
            quesChunkOne = reply[0:posIs]
            quesChunkTwo = reply[posOf+1:posBreakEnd]
            
            print "ansChunkOne :",ansChunkOne
            print "ansChunkTwo :",ansChunkTwo
            print "quesChunkOne :",quesChunkOne
            print "quesChunkTwo :",quesChunkTwo
            
            # This is the case when question is say : "Is New Delhi the capital of India ?" and the matched answer is 
            # "New Delhi is the capital of India". Then answer is yes, because all chunks match           
            if ansChunkOne == quesChunkOne and ansChunkTwo == quesChunkTwo:
                print "Case 1"
                print "Yes"
            # This is the case when question is say : "Is patna the capital of India ?" and the matched answer is 
            # "New Delhi is the capital of India". Then {Patna} and {New Delhi} are compared since {India} is common to both
            elif ansChunkOne != quesChunkOne and ansChunkTwo == quesChunkTwo:
                print "Case 2"
                print "No"
            elif ansChunkOne != quesChunkOne and ansChunkTwo != quesChunkTwo:
                print "Case 3"
                print "I don't know, but I know one thing that ", answer
            # This is the case when question is say : "Is New Delhi the capital of USA ?" and the matched answer is 
            # "New Delhi is the capital of India". Then {India} and {USA} are compared. Since some states have the same city as
            # their capitals hence it's not possible to answer correctly.            
            else:
                print "Case 4"
                print "I don't know, but I know one thing that ", answer          
     
    def respond(self,query):
        query=query.lower()
        response=""
        queryWords=tags.give_relevant_words(query)
        print "The Query Words are :", queryWords
        
        # Find the closest match to the answer
        (qIndex,qConf)=self.closest_question(queryWords)
        
        if qIndex!= None and qConf>self.THRESHOLD:
            print "Hi"
            res = self.answer_from(queryWords,qIndex)
            print "Hey"
            querType = self.type(query)
            
            print res
            print "Index :",qIndex
            print "Question closest to your query is :",self._quesList[qIndex],qConf
            print "The response to your question is :"
            self.answer_construct(querType, query, res)
            #Find Question Word using pos Tagger
            #Find corresponding template
            #In, after
            #Search for "in" in the answer
            #and start your answer from the next word
            #till???
            #    the tag of the word is in self.SENTENCE_DIVIDERS
            #print the Answer of the question

        else:
            newQuery=raw_input("Cannot identify a good source to answer your question.\nCan you please add some more information?\n")
            #Remove common words
            query=nltk.word_tokenize(query.lower())
            newQuery=nltk.word_tokenize(newQuery.lower())
            combinedquery=query+newQuery
            cquery = []
            [cquery.append(x) for x in combinedquery if x not in cquery]
            combinedquery=cquery
            self.respond(' '.join(combinedquery))

if __name__ == "__main__":
    autofaq=AutoFAQ()
    
    query=raw_input("Please enter your Query\n");
    print "The Query given as input is :",query
    autofaq.type(query);
    autofaq.respond(query);
