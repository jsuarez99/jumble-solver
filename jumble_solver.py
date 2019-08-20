from input_puzzles import puzzleInputs
from pyspark.sql import SparkSession
from itertools import product
import json
import re

spark = SparkSession.builder.appName("Jumble Solver").getOrCreate()
sc = spark.sparkContext

#Load the json data into a dictionary
freq_dict = {}
with open("freq_dict.json", 'r') as jsonFile:
	freq_dict = json.load(jsonFile)
	
#Helper function to get all words of length n (wordLength) from the dictionary 
#Runs fast enough with this data set, in production this would work better as a spark dataframe
def getWordsFromDictionary(wordLength):
	return set([word for word in freq_dict.keys() if len(word) == wordLength])
	
#Function that returns true if all characters in needle are in the variable haystack.
#For each loop through needle's characters, a character from haystack is removed.
def checkIfWordInAnsStr(needle, haystack):
	for chr in list(needle):
		if chr not in haystack:
			return False
		else:
			haystack = re.sub(chr,"",haystack,count=1)
			
	return True

#Go through the tuple of puzzle input objects and begin solving them
for puzzle in puzzleInputs:
	jumbles = puzzle.jumbles
	answerLengths = tuple(puzzle.answerWordLengths)
	circledLettersAns = []  #Holds all circled letters for each solved jumble
	
	#Loop through the keys and values in jumbles
	#Keys are jumbled letters, values are indices of circled letters
	for (key,val) in jumbles.items():
		#Get all unique permutations of the jumble letter set
		letterSetPermutations = set(permutations(key))
		
		#Get all words in the dictionary that are the same length as the jumble
		#  -The filter removes words with characters not in the jumble
		#  -map creates a tuple of (word, frequency_score, string of circled characters)
		#  -sort will assign a value of 'infinity' to words with score of 0 since they are infrequent. This
		#   will make them last in the ordering
		possibleWordResults = sc \
			.parallelize( getWordsFromDictionary(len(key)) , 16 ) \
			.filter( lambda word: checkIfWordInAnsStr(word, key.lower()) ) \
			.map( lambda word : (word, freq_dict.get(word), "".join([ list(word)[i-1] for i in val ])) ) \
			.sortBy( lambda wordTup: float('inf') if wordTup[1] == 0 else wordTup[1] ) \
			.collect()
		
		#keep track of all the possible word results for each jumble. This will be a list of list of tuples.
		circledLettersAns.append(possibleWordResults)
	

	#Begin searching for the final answer
	foundFinalAnswers = []    #possible final answers are stored in this list
	loopCount = 1             #loop count is used for determining whether to filter out words later
	
	#the itertools.product function will go through every combination in the list of possible answers
	for answersPermutation in product(*circledLettersAns):
		#create a list of all jumble answers
		jumbleAnswers = list(map(lambda x: x[0], answersPermutation))
		#join all answers in a single string to using in function "checkIfWordInAnsStr"
		ansStr = "".join(list(map(lambda x: x[2], answersPermutation)))
		#Get the total score of this set of answers
		ansSetScore = sum(ansSet[1] for ansSet in answersPermutation)
		
		#If the total set of answers scores is 0 and we already have found some possible answers,
		#skip this set since the best answer has already been found.
		if ansSetScore == 0 and len(foundFinalAnswers) > 0:
			continue
		
		#Filter out the possible words by using the joined ansStr to remove words in possibleWords that
		#couldn't exist together in the answer
		possibleAnswers = []
		for ansLen in answerLengths:
			possibleWords = getWordsFromDictionary(ansLen)
			
			#First filter by if the word is in the answer string
			#Next map to (word, frequency_score)
			#Then sort by frequency_score. Again, 0s are set to 'inf' and made last in ascending sort
			ansContains = sc \
				.parallelize( possibleWords, 16 ) \
				.filter( lambda word : checkIfWordInAnsStr(word, ansStr) ) \
				.map( lambda word : (word, freq_dict.get(word)) ) \
				.sortBy( lambda wordTup: float('inf') if wordTup[1] == 0 else wordTup[1] ) \
				.collect()
			
			if len(ansContains) == 0:
				break
			else:
				possibleAnswers.append(ansContains)
		
		
		#Now check the words to see if they fit in the final answer
		if len(possibleAnswers) == len(answerLengths):
			
			#Steps here are:
			#  -Create an RDD of the product of the possible answers found in the last for loop
			#  -filter by the sum of their frequency scores - if 'inf', filter it out. If no answer has been found so far (after the first loop), don't filter anything.
			#   Why after the first? Because the first had the highest score and produced nothing, so its time to stop filtering.
			#  -filter with checkIfWordInAnsStr again, this time using a joined string of all the possible answer words
			#  -map to a tuple of (joined sentence, score, answers used to created the final sentence)
			#  -sort by the best score
			#  -take the top answer 				.filter( lambda sentence: True if loopCount > 1 and len(foundFinalAnswers) == 0 else sum(float('inf') if n == 0 else n for _,n in sentence) != float('inf') )\
			bestPossible = sc \
				.parallelize( set(product(*possibleAnswers)), 1000) \
				.filter( lambda sentence: checkIfWordInAnsStr("".join(list(map(lambda x : x[0], sentence))), ansStr[:]) ) \
				.map( lambda sentence: ( " ".join(list(map(lambda x : x[0], sentence))), sum(float('inf') if n == 0 else n for _,n in sentence), answersPermutation ) ) \
				.sortBy( lambda wordTup: wordTup[1] ) \
				.take(1)
			
			if len(bestPossible) > 0:
				foundFinalAnswers.append(bestPossible[0])
				
		loopCount += 1

	#Print out the final results
	if len(foundFinalAnswers) > 0:
		print("=====\nmydebug: jumbles: {}".format(jumbles))
		print("mydebug: best answers: {}".format(" ".join(list(map(lambda wordScore: wordScore[0], foundFinalAnswers[0][2])))) )
		print("mydebug: best final answer: {}".format(foundFinalAnswers[0][0]) )
	else:
		print("mydebug: no answers found")