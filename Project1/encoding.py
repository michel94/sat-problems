from formula import *

auxCount = 0

def ExactlyOnce(l):
	exp = Formula()

	atLeast = Clause()
	for i in l:
		atLeast |= i
	exp &= atLeast
	for i in range(len(l)):
		for j in range(len(l)):
			if i != j:
				exp &= -l[i] | -l[j]

	return exp

def AtMost(l, k):
	global expression, auxCount

	exp = Formula()
	n = len(l)
	size = n
	S = [[Var('S(' + str(auxCount) + ')_' + str(i) + "_" + str(j)) for j in range(1, min(i+1, k+2) )] for i in range(1, size+1 ) ]
	auxCount += 1
	
	for i in range(size):
		exp &= (-l[i] | S[i][0])
		if k < i:
			exp &= (-S[i][k])

	for i in range(1, size):
		for j in range(i):
			if j < k+1:
				exp &= (-S[i-1][j] | S[i][j])

	for i in range(1, size):
		for j in range(1, i+1):
			if j < k+1:
				exp &= (-l[i] | -S[i-1][j-1] | S[i][j])
	
	return exp


def WeightedAtMost(l, w, k):
	global expression, auxCount
	
	exp = Formula()
	n = len(l)
	S = [[Var('S(' + str(auxCount) + ')_' + str(i) + "_" + str(j)) for j in range(k+1)] for i in range(1, n+1 ) ]
	auxCount += 1
	
	append = exp.clauses.append
	for j in range(k):
		if j < w[0]:
			append(-l[0] | S[0][j])
		else:
			exp &= -S[0][j]


	exp &= -S[0][k]
	for i in range(1, n):
		exp &= -S[i][k]
		for j in range(0, k+1):
			if j < w[i]:
				append(-l[i] | S[i][j])
			append(-S[i-1][j] | S[i][j])
	
	for i in range(1, n):
		for j in range(0, k-w[i]+1):
			append(-l[i] | -S[i-1][j] | S[i][j+w[i]])

	return exp

