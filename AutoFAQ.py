#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk
import params
import tags
import qna_parser
import templateParser
import sys
import math
import argparse
import type_similarity
import xml.dom.minidom as minidom
import sys
from nltk.corpus import wordnet
import wiki

class AutoFAQ:
    _quesList=[]
    _ansList=[]
    _quesListProcessed=[]
    _porter = nltk.PorterStemmer()
    _wnl = nltk.WordNetLemmatizer()
    _templates=[]
    _qtypes=[]
    _debug = False
    _matrix = {}
    #WEIGHT_DICTIONARY=0.6
    #WEIGHT_STEMMED=0.8
    #Threshold for finding closest question
    THRESHOLD=1
    CLOSENESS_THRESHOLD=0.1
    CLOSENESS_RATIO=0.1
    QUESTION_WORD_TAGS=['WP','WRB']
    SENTENCE_DIVIDERS=['']
    _stopwords=[]

    def preprocess_query(self, query):
        #Strip any question marks if there
        query=query.encode().lower()
        query=query.replace("?","")
        
        tokens=nltk.word_tokenize(query)
        #Remove stopwords
        tokens=filter(lambda t:t.lower() not in self._stopwords, tokens)

        #Stem each word
        tokens=map(lambda t:self._wnl.lemmatize(t), tokens)
        return tokens
        
    def  __init__(self):
        print("Welcome to AutoFAQ. Initializing AutoFAQ for you ...")
        
        parser = argparse.ArgumentParser()
        parser.add_argument("-d","--debug",help="Run the program in debug mode", action="store_true")
        args = parser.parse_args()
        self._debug = args.debug

        #Initialized the list of stopwords
        self._stopwords=nltk.corpus.stopwords.words('english')

        #Parse the xml
        (self._quesList,self._ansList)=qna_parser.parse_xml(params.faqFile)
        #self._quesList=map(lambda ques:ques.lower(), self._quesList)
        #self._ansList=map(lambda ques:ques.lower(), self._ansList)
        self._quesListProcessed = map(lambda q:self.preprocess_query(q), self._quesList)
        self._matrix=type_similarity.get_matrix_english(params.similarity_matrix_file)

        #Parse the templates
        (self._templates,self._qtypes)=templateParser.parse_xml(params.templateFile)
        if self._debug:
            print self._templates
            print self._qtypes

        output=self.validate_input_file()
        if not output:
            print "Input file not Valid."
            sys.exit(-1)
        else:
            print "Input file validated."

        return
        
    def validate_input_file(self):
        for q in self._quesList:
            t=self.type(q)
            if t == None:
                print "Couldn't find type",q
                
            if self._debug:
                print "Q:",q,"Type:",
        return True

    '''
    Four similarity measures viz. Coverage, Question Type Similarity, Term Vector Similarity and Semantic Similarity
    '''
    
    #Score b/w l1 and l2 list of words
    def coverage_score(self,l1,l2):
        '''
        score1=len(set(l1).intersection(l2))

        l1_stemmed=map(lambda a:self._porter.stem(a),l1)
        l2_stemmed=map(lambda a:self._porter.stem(a),l2)
        score2=set(l1_stemmed).intersection(l2_stemmed)*self.WEIGHT_STEMMED
        '''

        #Use Wordnet Lemmatizer for stemmed keyword Matching
        #l1_stemmed=map(lambda a:self._wnl.lemmatize(a),l1)
        #l2_stemmed=map(lambda a:self._wnl.lemmatize(a),l2)
        #Already stemmed l1 and l2 now using wordnet lemmatizer

        #The percentage of user question terms that appear in the FAQ question.
        score=len(set(l1).intersection(l2))
        return float(score)/len(l1)

    def ques_type_score(self, l1, l2):
        '''
        Question type score based on the matrix in the file as given in params configuration.
        '''
        type1=self.type(l1)
        type2=self.type(l2)
        if (type1 != None) and (type2 != None):
            return self._matrix[type1][type2]
        else:
            return 0

    def term_vector_similarity(self,l1,l2):
        '''
        Term vector similarity is the following cosine measure
        say v=(v1,v2...vn) #processed terms for the query
        say w=(w1,w2...wn) #processed terms for the question

        cosO = v.w/(square root of len(v) and len(w))
        '''
        score=len(set(l1).intersection(l2))
        return float(score)/math.sqrt(len(l2)*len(l1))

    def semantic_similarity(self,l1,l2):
        #Use wordnet to find the semantic similarity for two different Questions
        #Take into account all synonyms and all (eg. for What?)

        l1_with_dictionary=reduce(lambda x,y:x+y, map(lambda word:[l.name for s in wordnet.synsets(word) for l in s.lemmas],l1))
        l1_with_dictionary=map(lambda ele:ele.lower(), l1_with_dictionary)
        #^^ Returns duplicated elements as well. So we need to remove the duplicates. Converting into set does that
        
        l2_with_dictionary=reduce(lambda x,y:x+y, map(lambda word:[l.name for s in wordnet.synsets(word) for l in s.lemmas],l2))
        l2_with_dictionary=map(lambda ele:ele.lower(), l2_with_dictionary)
        #^^ Returns duplicated elements as well. So we need to remove the duplicates. While taking intersection the same is handled

        score1=len(set(l1_with_dictionary).intersection(l2))
        score2=len(set(l2_with_dictionary).intersection(l1))

        return float(max(score1,score2))/min(len(l2),len(l1))
        #*self.WEIGHT_DICTIONARY

    #Returns the index of the closest_match with the score of it
    def closest_question(self,queryWords):
        scoreList=map(lambda ques: self.score(queryWords, ques), self._quesListProcessed)
        maxScore=max(scoreList)

        if self._debug:
            print scoreList
        return (scoreList.index(maxScore),maxScore)
        #Check if there are some questions to close to the highest scoring function in the scoreList
        #if (len(filter(lambda x: x>= maxScore-self.CLOSENESS_THRESHOLD, scoreList)) < len(self._quesList)*self.CLOSENESS_RATIO ):
        #    return (scoreList.index(maxScore),maxScore)
        #else:
        #    return (None,None)

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
        query=query.replace("?"," ?") #Append a space before the question mark
        query=query.lower().split()
        query_tags=nltk.pos_tag(query)
        index = 0
        matchDone = False		
        try:
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
                                    print "Question mark was seem to be missing. Appended the same, and reasking your query to the system"
                                    [tempTags].pop(0)
                                    exit = True
                                    matchDone = True
            return self._qtypes[index]
        except:
            return None
    
    def closest_question_index (self,query):
        query=query.lower()
        queryWords=self.preprocess_query(query)
        typeScore=map(lambda ques: self.ques_type_score(query, ques), self._quesList)
        coverageScore=map(lambda ques: self.coverage_score(queryWords, ques), self._quesListProcessed)
        semanticScore=map(lambda ques: self.semantic_similarity(queryWords, ques), self._quesListProcessed)
        termVectorScore=map(lambda ques: self.term_vector_similarity(queryWords, ques), self._quesListProcessed)
        scoreList=[]
        for i in xrange(len(typeScore)):
            scoreList.append(0.25*(float(typeScore[i])+float(coverageScore[i])+float(semanticScore[i])+float(termVectorScore[i])))
			
        return self._quesList[scoreList.index(max(scoreList))]

		
    def respond(self,query):
        query=query.lower()
        response=""
        queryWords=self.preprocess_query(query)
        
        # Find the closest match to the answer
        #(qIndex,qConf)=self.closest_question(queryWords)

        #Only typeScore takes the query, all other takes the processed query and the words
        typeScore=map(lambda ques: self.ques_type_score(query, ques), self._quesList)
        coverageScore=map(lambda ques: self.coverage_score(queryWords, ques), self._quesListProcessed)
        semanticScore=map(lambda ques: self.semantic_similarity(queryWords, ques), self._quesListProcessed)
        termVectorScore=map(lambda ques: self.term_vector_similarity(queryWords, ques), self._quesListProcessed)		
        
        scoreList=[]
        for i in xrange(len(typeScore)):
            scoreList.append(0.25*(float(typeScore[i])+float(coverageScore[i])+float(semanticScore[i])+float(termVectorScore[i])))
                
        if self._debug:
            print "Type Score List:",typeScore
            print "Coverage Score List:",coverageScore
            print "Semantic Similarity List:",semanticScore
            print "Term Vector Score List:",termVectorScore
            print "Final Score List:",scoreList
            

        scores_sorted=sorted(scoreList, reverse=True)

        qConf=scores_sorted[0]
        retConf=qConf

        if (qConf < params.MIN_THRESHOLD):
            print "Sorry, no match to your query.\n"
            return qConf
        
        if (qConf < params.RVP_THRESHOLD):
            print "Sorry, no appropriate match found. Additional info is as follows.\n"
            
        if (qConf==scores_sorted[1]):
            print "Both of the following FAQs are the closest match to your query\n"
            qIndex=scoreList.index(qConf)
            print "Q1:",self._quesList[qIndex]
            print "A1:",self._ansList[qIndex]

            qIndex=scoreList.index(qConf,qIndex+1)
            print "Q2:",self._quesList[qIndex]
            print "A2:",self._ansList[qIndex]
            return retConf
        
        qIndex=scoreList.index(qConf)

        if self._debug:
            print scoreList

        #qIndex=?
        quesType = self.type(query)

        if quesType != None:
            print "The type of your question is : ", quesType,"\n"
        else:
            print "Your question doesn't seem to fit any question type"
            
        if self._debug:
            print "The Query Words are :", queryWords
            print "Index :",qIndex

        print "The closest FAQ pair to your query is following."
        print "Q:",self._quesList[qIndex]
        print "A:",self._ansList[qIndex]
        print "The confidence that I have regarding this question match on the scale of 100 is :", qConf*100,"\n"

        qConf1=scores_sorted[1]
        if qConf1 > params.RVP_THRESHOLD:
            print "RELATED FAQ"

            qIndex=scoreList.index(qConf1)
            print "Q:",self._quesList[qIndex]
            print "A:",self._ansList[qIndex]
            print "Confidence:",qConf1*100,"\n"

        qConf2=scores_sorted[2]
        if qConf2 > params.RVP_THRESHOLD:
            qIndex=scoreList.index(qConf2)
            if qConf2 == qConf1:
                qIndex=scoreList.index(qConf2,qIndex+1)
            print "Q:",self._quesList[qIndex]
            print "A:",self._ansList[qIndex]
            print "Confidence:",qConf2*100,"\n"

        return qConf
        
        #DEPRECATED: Since, all the values now will be normalized this Threshold is not needed. And we can check against a constant value.
        """
        if qIndex!= None and qConf>self.THRESHOLD:
            res = self.answer_from(queryWords,qIndex)
            querType = self.type(query)
            print "The type of your question is : ", querType
            if self._debug:
                print "The Query Words are :", queryWords
                print "Index :",qIndex
            print "The closest question in the FAQ is :",self._quesList[qIndex]
            print "The confidence that I have regarding this question match is :", qConf
            print "The answer in the FAQ is :",res

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
        """

    def respond_wiki(self,query):
        url=raw_input("Please enter the URL of the page of the wikipedia where information should be searched from (like http://en.wikipedia.org/wiki/Google_Summer_of_Code):\n")
        tokens=url.split('/')
        subject=tokens[len(tokens)-1]
        pWiki = wiki.Wiki(subject)
        pWiki.getPage()
        
        lines=pWiki.getRawText()

        query=query.lower()
        queryWords=self.preprocess_query(query)
        linesWords=map(lambda line:self.preprocess_query(line), lines)
        
        # Find the closest match to the answer
        #(qIndex,qConf)=self.closest_question(queryWords)

        #Only typeScore takes the query, all other takes the processed query and the words        
        coverageScore=map(lambda lineWords: self.coverage_score(queryWords, lineWords), linesWords)
        semanticScore=map(lambda lineWords: self.semantic_similarity(queryWords, lineWords), linesWords)
        termVectorScore=map(lambda lineWords: self.term_vector_similarity(queryWords, lineWords), linesWords)
        
        scoreList=[]
        for i in xrange(len(coverageScore)):
            scoreList.append(0.33*(float(coverageScore[i])+float(semanticScore[i])+float(termVectorScore[i])))
                
        if self._debug:
            print "Coverage Score List:",coverageScore
            print "Semantic Similarity List:",semanticScore
            print "Term Vector Score List:",termVectorScore
            print "Final Score List:",scoreList
            
        scores_sorted=sorted(scoreList, reverse=True)

        qConf=scores_sorted[0]
        retConf=qConf

        if (qConf < params.RVP_THRESHOLD):
            print "Sorry, no match to your query.\n"
            return qConf

        if self._debug:
            print scoreList

        print "Informative Lines"
        qIndex=scoreList.index(qConf)
        i=1
        while qConf > params.RVP_THRESHOLD:
            print str(i)+":",lines[qIndex]
            print "Confidence Level (out of 100)",qConf*100,"\n"
            i=i+1
            qConf_next=scores_sorted[i]
            if i==5:
                break
            if qConf == qConf_next:
                qIndex=scoreList.index(qConf,qIndex+1)
            else:
                qIndex=scoreList.index(qConf_next)
                qConf=qConf_next
                
        return retConf

    
if __name__ == "__main__":
    autofaq=AutoFAQ()
    #autofaq._debug=True

    query=raw_input("Please enter your Query.\n");
    if autofaq._debug:
        print "The Query given as input is :",query

    #autofaq.type(query);
    while True:
        confLevel=autofaq.respond(query);
        if confLevel < params.RVP_THRESHOLD:
            query_yesno=raw_input("Do you want to search Wikipedia for the same query? Please type y/n.\n");
            if query_yesno.lower().startswith("y"):
                autofaq.respond_wiki(query);
        try:
            query=raw_input("Please enter your Query. Press Ctrl+c to break.\n");
        except KeyboardInterrupt:
            break;
