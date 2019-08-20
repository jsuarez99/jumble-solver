#The class JumblePuzzle will be an object with a dictionary for the jumbles
#and a tuple for the lengths of each word in the answer.
#The jumbles dictionary will have a key of jumbled letters and a value of a
#tuple of circled letters to be used in the final answer.
class JumblePuzzle:
	jumbles = {}
	answerWordLengths = ()
	
	def __init__(self,jumblesDict, answerWordLengths):
		self.jumbles = jumblesDict
		self.answerWordLengths = answerWordLengths

#build out each object
puzzle1 = JumblePuzzle({
		"NAGLD" : (2,4,5),
		"RAMOJ" : (3,4),
		"CAMBLE" : (1,2,4),
		"WRALEY" : (1,3,5)
		},
		(3,4,4)
	)
	
puzzle2 = JumblePuzzle({
		"BNEDL" : (1,5),
		"IDOVA" : (1,4,5),
		"SEHEYC" : (2,6),
		"ARACEM" : (2,5,6)
		},
		(3,4,3)
	)
	
puzzle3 = JumblePuzzle({
		"SHAST" : (1,4,5),
		"DOORE" : (1,2,4),
		"DITNIC" : (1,2,3),
		"CATILI" : (1,3,6)
		},
		(4,8)
	)
	
puzzle4 = JumblePuzzle({
		"KNIDY" : (1,2),
		"LEGIA" : (1,3),
		"CRONEE" : (2,4),
		"TUVEDO" : (1,6)
		},
		(8,)
	)
	
puzzle5 = JumblePuzzle({
		"GYRINT" : (1,2,4),
		"DRIVET" : (3,6),
		"SNAMEA" : (1,6),
		"CEEDIT" : (2,4,6),
		"SOWDAH" : (1,4),
		"ELCHEK" : (2,6)
		},
		(6,8)
	)
	
#Now build a tuple of the puzzle inputs
puzzleInputs = (puzzle1, puzzle2, puzzle3, puzzle4, puzzle5)