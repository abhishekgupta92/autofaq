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


if __name__ == "__main__":
    quesList=[]
    ansList=[]
    (quesList,ansList)=parse_xml("input.xml")
    print "First Q/A Pair"
    print "Q:",quesList[0]
    print "A:",ansList[0]
    print "Last Q/A Pair"
    print "Q:",quesList[len(quesList)-1]
    print "A:",ansList[len(quesList)-1]
