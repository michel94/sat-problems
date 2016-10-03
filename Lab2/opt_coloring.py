#!/usr/bin/python

from math import ceil, log2, sqrt
from functools import reduce
import operator
import sys
sys.path.append('..')

from formula import *

SIZE = 0
colors = 1

def readGraph(filename):
	global SIZE
	graph = []
	with open(filename) as f:
		lines = f.readlines()
		for line in lines:
			if line[0] == 'p':
				line = line.split()
				SIZE = int(line[2])
				graph = [[] for i in range(SIZE)]
			elif line[0] == 'e':
				_, s, e = line.split()
				s = int(s)-1
				e = int(e)-1
				graph[s].append(e)
				graph[e].append(s)
			else:
				pass
		
		return graph

args = []
namedArgs = {}
for i in sys.argv:
	if i.startswith('--'):
		ind = i.find('=')
		namedArgs[i[2:ind]] = i[ind+1:]
	else:
		args.append(i)

filename = args[1]
graph = readGraph(filename)
formula = None

while True:
	nbits = ceil(log2(colors))
	if nbits == 0:
		nbits = 1
	print("Colors:", colors)
	graphColors = [[Var("C" + str(i) + "-V" + str(k)) for k in range(nbits)] for i in range(SIZE)]
	formula = Formula()
	formula &= graphColors[0][0]

	for x in range(colors, 2**nbits):
		enc = [int(b) for b in bin(x)[2:]]
		enc = [0] * (nbits - len(enc)) + enc

		for i in range(SIZE):
			exp_ = Clause()
			for c, v in zip(graphColors[i], enc):
				if v:
					exp_ |= -c
				else:
					exp_ |= c
			formula &= exp_

	for i in range(SIZE):
		for j in graph[i]:
			if i < j:
				for x in range(colors):
					enc = [int(b) for b in bin(x)[2:]]
					enc = [0] * (nbits - len(enc)) + enc

					exp = Clause()
					for c1, c2, v in zip(graphColors[i], graphColors[j], enc):
						if v:
							exp |= -c1 | -c2
						else:
							exp |= c1 | c2
					
					formula &= exp

	if 'solver' in namedArgs:
		solver = Solver(namedArgs['solver'])
	else:
		solver = Solver()
	solution = solver.solve(formula)

	if not solution.success:
		colors += 1
	else:
		break

coloring = []
nbits = ceil(log2(colors))
for i in range(SIZE):
	color = sum([(2**(nbits-1-k) )*solution[j] for k, j in enumerate(graphColors[i])])
	coloring.append(color)
	#print(i, color)
print(coloring)


