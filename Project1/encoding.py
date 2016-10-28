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
	if len(l) < sum(w)*10:
		return Totalizer(l, w, k)
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

totals = []

def Totalizer(l, w, k):
	global auxCount, totals
	groups = []
	for i in range(len(l)):
		groups.append( {w[i]: l[i]} )

	exp = Formula()
	varCount = 1

	while len(groups) >= 2:
		ng = {}
		gr1 = groups[0]
		gr2 = groups[1]
		del groups[0]
		del groups[0]
		#print(len(groups), len(gr1), len(gr2))
		for b in gr2:
			if b not in ng:
				ng[b] = Var('T(%d)%d' % (auxCount, varCount))
				totals.append(ng[b])
				varCount += 1
				#print("clause:", b, ng[b])
			exp &= (-gr2[b] | ng[b])

		for a in gr1:
			if a not in ng:
				ng[a] = Var('T(%d)%d' % (auxCount, varCount))
				totals.append(ng[a])
				varCount += 1
				#print("clause:", a, ng[a])
			exp &= (-gr1[a] | ng[a])
			for b in gr2:
				if a+b not in ng:
					ng[a+b] = Var('T(%d)%d' % (auxCount, varCount))
					totals.append(ng[a+b])
					varCount += 1
				#print("clause:", a, b, a+b, ng[a+b])
				exp &= (-gr1[a] | -gr2[b] | ng[a+b])

		clean = {}
		for i in ng:
			if i > k:
				exp &= -ng[i]
			else:
				clean[i] = ng[i]

		groups.append(clean)

	auxCount += 1

	return exp

