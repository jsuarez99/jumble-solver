# jumble-solver
A pyspark script that will attempt to solve newspaper Jumble puzzles

## To Run

This was run on Ubuntu for Windows Subystem. I used the script `spark-submit.sh` in order to set up spark on my local computer and run the python script via `spark-submit`. My script's output can be grepped out of the command line by filtering for 'Jumble Solver:' lines.

## Output

My script attempts to solve the jumbles by looking for words with the lowest score that is not 0. If none are available, then whatever is available is ued. For the final jumble, I attempt to use all combinations of circled letters of all possible answers and then try to find the lowest score that is not zero for the final answer. For some puzzles this works (Puzzle 3: Addition) but for others it is close enough or completely wrong (Puzzle 1: "Job Need Wall" instead of "Jab Well Done").

```
Jumble Solver: jumbles: {'WRALEY': (1, 3, 5), 'RAMOJ': (3, 4), 'NAGLD': (2, 4, 5), 'CAMBLE': (1, 2, 4)}
Jumble Solver: best answers: lawyer major gland becalm
Jumble Solver: best final answer: job need wall
Jumble Solver: jumbles: {'BNEDL': (1, 5), 'SEHEYC': (2, 6), 'IDOVA': (1, 4, 5), 'ARACEM': (2, 5, 6)}
Jumble Solver: best answers: blend cheesy avoid camera
Jumble Solver: best final answer: bad hair day
Jumble Solver: jumbles: {'DOORE': (1, 2, 4), 'DITNIC': (1, 2, 3), 'CATILI': (1, 3, 6), 'SHAST': (1, 4, 5)}
Jumble Solver: best answers: rodeo indict italic stash
Jumble Solver: best final answer: dish scenario
Jumble Solver: jumbles: {'CRONEE': (2, 4), 'LEGIA': (1, 3), 'KNIDY': (1, 2), 'TUVEDO': (1, 6)}
Jumble Solver: best answers: encore agile dinky devout
Jumble Solver: best final answer: addition
Jumble Solver: jumbles: {'CEEDIT': (2, 4, 6), 'DRIVET': (3, 6), 'SNAMEA': (1, 6), 'ELCHEK': (2, 6), 'SOWDAH': (1, 4), 'GYRINT': (1, 2, 4)}
Jumble Solver: best answers: deceit divert seaman kechel shadow trying
Jumble Solver: best final answer: divert tentless
```