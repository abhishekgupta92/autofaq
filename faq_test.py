import AutoFAQ
import unittest
import qna_parser
import params
import type_similarity

'''
The Type finding function is rule based, so clearly there
will be many instances of the question where the answer
would be known. Below is the class of representative samples
where the results should be as described in the structure.
'''
class TypeTest (unittest.TestCase):
	knownTypes = (	('Do you like to swim?','ynq'),
					('What is it like to work in Google Summer of Code?','def'),
					('When is right time to talk to you?','time'),
					('Where does President resides?','loc'),
					('Why is Earth round?','rsn'),
					('How do we die?','prc'),
				)
	
	def testToFindTypes(self):
		'''use type function to find the type of the given query'''
		autofaq=AutoFAQ.AutoFAQ()
		for question,type in self.knownTypes:
			result=autofaq.type(question)
			self.assertEqual(type,result)

'''
Questions in input.xml should be the closest to themselves
'''
class IdenticalQuestions (unittest.TestCase):
	_quesList=[]
	_ansList=[]
	
	def testToCheckIdenticalQueriesToFAQ(self):
		(self._quesList,self._ansList)=qna_parser.parse_xml(params.faqFile)
		'''use closest_question_index function to find the type of the given query'''
		autofaq=AutoFAQ.AutoFAQ()
		for ques in self._quesList:
			closest_ques=autofaq.closest_question_index(ques)
			self.assertEqual(ques,closest_ques)

'''
Check the matrix generated about the type similarities
'''
class checkTypeMatrixValidity (unittest.TestCase):
	matrix=type_similarity.get_matrix_english("ques_similarity_matrix.txt")
	keys=matrix.keys()
	length=len(matrix[keys[0]])
		
	def checkRows(self):
		for key in keys:
			l=len(matrix[key])
			self.assertEqual(length,l)
			
	def checkDimensions(self):
		height=len(matrix)
		self.assertEqual(length,height)
	
	def checkSimilarity(self):
		for i in keys:
			for j in keys:
				val1=matrix[i][j]
				val2=matrix[j][i]
				self.assertEqual(val1,val2)

if __name__ == "__main__":
    unittest.main()