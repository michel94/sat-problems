#!/usr/bin/python
from satispy import Variable, Cnf
from satispy.solver import Minisat
from math import sqrt
import sys
sys.path.append('..')
from formula import *

SIZE = 0
colors = 1
expression = Formula()

def readGraph(filename):
	global SIZE
	graph = []
	with open(filename) as f:
		lines = f.readlines()
		for line in lines:
			if line[0] == 'c':
				pass
			elif line[0] == 'p':
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


def ExactlyOnce(l):
	global expression

	atLeast = Clause()
	for i in l:
		atLeast |= i
	expression &= atLeast
	for i in range(len(l)):
		for j in range(len(l)):
			if i != j:
				expression &= -l[i] | -l[j]

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

	print("Colors:", colors)
	graphColors = [[Var("V" + str(i) + str(k)) for k in range(colors)] for i in range(SIZE)]
	expression = Formula()

	for i in range(SIZE):
		ExactlyOnce(graphColors[i])
		for j in graph[i]:
			if i < j:
				for k in range(colors):
					expression &= (-graphColors[i][k] | -graphColors[j][k])
		
	solver = Solver()
	solution = solver.solve(expression)

	if not solution.success:
		colors += 1
	else:
		break

for i in range(SIZE):
	for k, j in enumerate(graphColors[i]):
		if solution[j]:
			#print(i, k)
			pass


