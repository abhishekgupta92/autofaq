#!/usr/bin/env python
# -*- coding: utf-8 -*-

import params
import nltk

#Remove elements from the list (list of tuples (string,tag)) where the tag belongs to params.TAGS
def rem_tag(tlist):                                     # function to remove tags
	return filter(lambda tup:tup[1] not in params.TAGS, tlist)

def give_relevant_words(query):
    #Tokenize the query
    tokens=nltk.word_tokenize(query)
    #POS Tag the query
    taggedList=nltk.pos_tag(tokens) #Returns a list of tuples
    #Remove words with unnecessary tags
    return map(lambda a:a[0],rem_tag(taggedList))