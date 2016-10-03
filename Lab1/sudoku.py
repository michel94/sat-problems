from satispy import Variable, Cnf
from satispy.solver import Minisat
from math import sqrt


SIZE = 0
expression = Cnf()

def readSudoku(filename):
	global SIZE
	mat = []
	with open(filename) as f:
		lines = f.readlines()
		SIZE = int(lines[0])
		lines = lines[1:]
		for i in range(SIZE):
			l = lines[i]
			mat.append([int(i) for i in l.split()])
	return mat

def ExactlyOnce(l):
	global expression

	atLeast = Cnf()
	for i in l:
		atLeast |= i
	expression &= atLeast
	for i in range(len(l)):
		for j in range(len(l)):
			if i != j:
				expression &= -l[i] | -l[j]

mat = readSudoku("test2Sudoku.txt")

V = [[[Variable("V" + str(i) + str(j) + str(k)) for k in range(SIZE)] for j in range(SIZE)] for i in range(SIZE)]

sq = int(sqrt(SIZE))
for i in range(SIZE):
	for n in range(SIZE):
		ExactlyOnce([V[i][j][n] for j in range(SIZE)])
		ExactlyOnce([V[j][i][n] for j in range(SIZE)])
		ExactlyOnce([V[i][n][j] for j in range(SIZE)])
		y = (i//sq)*sq
		x = (i%sq)*sq
		ExactlyOnce([V[y+r][x+c][n] for c in range(sq) for r in range(sq)])

for r, row in enumerate(mat):
	for c, el in enumerate(row):
		if el != 0:
			expression &= V[r][c][el-1]

solver = Minisat()
solution = solver.solve(expression)
for i in range(SIZE):
	for j in range(SIZE):
		num = 0
		for k in range(SIZE):
			if solution[V[i][j][k]]:
				num = k+1

		print(num, end=" ")
	print()

