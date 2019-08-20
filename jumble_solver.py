from input_puzzles import puzzleInputs
from pyspark.sql import SparkSession
from itertools import product
import json
import re

spark = SparkSession.builder.appName("Jumble Solver").getOrCreate()
sc = spark.sparkContext

#Load the dictionary into an RDD of tuple( word, score )
freq_dict_df = sc.textFile('freq_dict.json', minPartitions=100) \
	.filter(lambda line: ':' in line) \
	.map(lambda line: ( re.sub("[\s\",]+", "", line), ) ) \
	.map(lambda line: ( line[0].split(":")[0], int(line[0].split(":")[1]) ) ) \
	.toDF() \
	.rdd
	
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
	
		#Get all words in the freq dictionary that are the same length as the jumble
		#  -The second filter removes words with characters not in the jumble
		#  -map creates a tuple of (word, frequency_score, string of circled characters)
		#  -sort will assign a value of 'infinity' to words with score of 0 since they are infrequent. This
		#   will make them last in the ordering
		possibleWordResults = freq_dict_df \
			.filter( lambda word: len(word[0]) == len(key) ) \
			.filter( lambda word: checkIfWordInAnsStr(word[0], key.lower()) ) \
			.map( lambda word : (word[0], word[1], "".join([ list(word[0])[i-1] for i in val ])) ) \
			.sortBy( lambda wordTup: float('inf') if wordTup[1] == 0 else wordTup[1] ) \
			.collect()
		
		#keep track of all the possible word results for each jumble. This will be a list of list of tuples.
		circledLettersAns.append(possibleWordResults)
	
	#Begin searching for the final answer
	foundFinalAnswers = []    #possible final answers are stored in this list
	
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
		
			#Check to see if all words of this length have already been grabbed
			skip = False
			if len(possibleAnswers) > 0:
				for wordList in possibleAnswers:
					if len(wordList[0]) == ansLen:
						possibleAnswers.append(wordList)
						skip = True
						break
			
			if skip:
				continue
			
			#First filter by if the word is in the answer string
			#Next map to (word, frequency_score)
			#Then sort by frequency_score. Again, 0s are set to 'inf' and made last in ascending sort
			ansContains = freq_dict_df \
				.filter( lambda word: len(word[0]) == ansLen ) \
				.filter( lambda word : checkIfWordInAnsStr(word[0], ansStr) ) \
				.map( lambda word : (word[0], word[1]) ) \
				.sortBy( lambda wordTup: float('inf') if wordTup[1] == 0 else wordTup[1] ) \
				.collect()
			
			if len(ansContains) == 0:
				break
			else:
				possibleAnswers.append(ansContains)
		
		#print("mydebug: {}".format(possibleAnswers))
		
		#Now check the words to see if they fit in the final answer
		if len(possibleAnswers) == len(answerLengths):
			
			#Steps here are:
			#  -Create an RDD of the product of the possible answers found in the last for loop
			#  -filter by the sum of their frequency scores - if 'inf', filter it out. If no answer has been found so far (after the first loop), don't filter anything.
			#   Why after the first? Because the first had the highest score and produced nothing, so its time to stop filtering.
			#  -filter with checkIfWordInAnsStr again, this time using a joined string of all the possible answer words
			#  -map to a tuple of (joined sentence, score, answers used to created the final sentence)
			#  -sort by the best score
			#  -take the top answer
			bestPossible = sc \
				.parallelize( set(product(*possibleAnswers)), 1000) \
				.filter( lambda sentence: checkIfWordInAnsStr("".join(list(map(lambda x : x[0], sentence))), ansStr[:]) ) \
				.map( lambda sentence: ( " ".join(list(map(lambda x : x[0], sentence))), sum(float('inf') if n == 0 else n for _,n in sentence), answersPermutation ) ) \
				.sortBy( lambda wordTup: wordTup[1] ) \
				.take(1)
			
			if len(bestPossible) > 0:
				foundFinalAnswers.append(bestPossible[0])
				

	#Print out the final results
	if len(foundFinalAnswers) > 0:
		print("=====\nJumble Solver: jumbles: {}".format(jumbles))
		print("Jumble Solver: best answers: {}".format(" ".join(list(map(lambda wordScore: wordScore[0], foundFinalAnswers[0][2])))) )
		print("Jumble Solver: best final answer: {}".format(foundFinalAnswers[0][0]) )
	else:
		print("Jumble Solver: no answers found")