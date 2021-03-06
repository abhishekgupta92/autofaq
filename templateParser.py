#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.dom.minidom as minidom

def parse_xml(fileName):
    templateList=[]
    typeList=[]
    dom=minidom.parse(fileName)
    rules=dom.getElementsByTagName('rule')
    
    for elements in rules:
        temp=elements.getElementsByTagName("template")[0].toxml().encode("utf-8").split()
        temp_tokened=temp[1:len(temp)-1]
        temp_sent=reduce(lambda x,y:x+y,temp_tokened)
        templateList.append(temp_sent);

    for node in rules:
        alist=node.getElementsByTagName('type')
        for a in alist:
            qtype= a.childNodes[0].nodeValue
            typeList.append(qtype);

    return (templateList,typeList)

if __name__ == "__main__":
    (templateList,typeList)=parse_xml("templates.xml")
    print "First Pair"
    print "Template:",templateList[0]
    print "Type:",typeList[0]
    print "Last Pair"
    print "Template:",templateList[-1:][0]
    print "Type:",typeList[-1:][0]
