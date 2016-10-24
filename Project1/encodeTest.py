#!/usr/bin/python3
import sys
sys.path.append('..')
from encoding import *

# 3a + 2b + 1c + 1d + 1e <= k
X = [Var('X_' + str(i)) for i in range(1,5+1)]

expression = Formula()
expression &= WeightedAtMost(X, [1, 1, 1, 1, 1], 3)
expression &= X[1]
expression &= X[2]
expression &= X[3]
#print(expression)

sol = Solver().solve(expression)
if sol.success:
	print([sol[x] for x in X])

	print('DP')
	c = 0
	for dp in range(len(dps)):
		c+=1
		for row in dps[dp]:
			r = []
			for v in row:
				r.append(sol[v])
			print(r)

		print('Vars:', [sol[i] for i in dpList[dp]])
	