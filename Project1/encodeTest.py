#!/usr/bin/python3
import sys
sys.path.append('..')
from encoding import *

# 3a + 2b + 1c + 1d + 1e <= k
X = [Var('X_' + str(i)) for i in range(1,5+1)]

expression = Formula()
expression &= Totalizer(X, [2, 2, 1, 2, 4], 4)
expression &= X[1]
#expression &= X[2]
expression &= X[3]
#print(expression)

sol = Solver().solve(expression)
if sol.success:
	print('Solution')
	print([sol[x] for x in X])
	#print([sol[x] for x in totals])