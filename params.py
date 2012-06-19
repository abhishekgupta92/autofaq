#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TAGS are the tags to be removed
TAGS=['$','SYM','"','(',')',',','--','.',':','CC','IN','LS','MD','POS','TO','``','VBZ','DT']

#Recall vs. Precision Threshold. That is increasing the value will increase the precision, but decreases recall. Should lie between 0 and 1.
RVP_THRESHOLD=0.5

templateFile="templates.xml"
faqFile="input.xml"
similarity_matrix_file="ques_similarity_matrix.txt"

