#!/usr/bin/env python
# -*- coding: utf-8 -*-

#it parses the xml file and creates a list of ques and answer and a nested list (ques_search) to search to match
import xml.dom.minidom as minidom

#read file and return a tuple of list of questions and answers
def parse_xml(fileName):
    quesList=[]
    ansList=[]
    doc=minidom.parse(fileName)
    faq=doc.getElementsByTagName('xml')[0].getElementsByTagName('qna')
    for elements in faq:
        ques_sent=elements.getElementsByTagName("ques")[0].childNodes[0].nodeValue
        ans_sent=elements.getElementsByTagName("ans")[0].childNodes[0].nodeValue
        quesList.append(ques_sent)
        ansList.append(ans_sent)
    return (quesList,ansList)

#	def return_list_of_questions
#	def return_list_of_answers
#	def read_first_question
#	def read_next_question
#	def read_nth_question
#	def read_first_answer
#	def read_next_answer
#	def read_nth_answer
