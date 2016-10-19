#!/usr/bin/python3

from math import *
import sys
sys.path.append('..')

from formula import *

auxCount = 0
dps = []
dpList = []
expression = Formula()

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

def AtMost(l, k):
	global expression, auxCount, dps

	exp = Formula()
	n = len(l)
	size = n
	S = [[Var('S(' + str(auxCount) + ')_' + str(i) + "_" + str(j)) for j in range(1, min(i+1, k+2) )] for i in range(1, size+1 ) ]
	#for s in S:
	#	print(s)
	dps.append(S)
	dpList.append(l)
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
	
	expression &= exp

nServers = int(input())
servers = [0] * nServers
for i in range(nServers):
	s = [int(i) for i in input().split()]
	servers[s[0]] = min(s[1], s[2])

servers = sorted(servers)
servers.reverse()

nVMs = int(input())
jobs = []
for i in range(nVMs):
	s = input().split()
	job = [int(i) for i in s[:-1]]
	if job[0] >= len(jobs):
		jobs.append([])
	if s[-1] == 'False':
		jobs[job[0]].append(False)
	else:
		jobs[job[0]].append(True)


while True:
	print('========= Trying with', nServers, 'servers =========')
	auxCount = 0
	dps = []
	dpList = []
	expression = Formula()
	#print(jobs)

	variables = [[[Var("VM" + str(job) + "-" + str(vm) + "-" + str(server) ) for server in range(nServers)] for vm in range(len(jobs[job]))] for job in range(len(jobs))]

	vmAssignment = [[] for i in range(nServers)]

	#print('Anti-collocation:')
	for iJob, job in enumerate(variables):
		for vm in job:
			ExactlyOnce(vm)
		collocation = jobs[iJob]
		exclude = []
		indexes = []
		for i in range(len(collocation)):
			if collocation[i]:
				indexes.append(i)
				exclude.append(job[i])

		#print('Job ' + str(iJob) + ":", indexes)

		for i in range(len(exclude)):
			for j in range(i+1, len(exclude)):
				for s in range(nServers):
					expression &= (-exclude[i][s] | -exclude[j][s])

	for job in variables:
		for vm in job:
			for i in range(len(vm)):
				vmAssignment[i].append(vm[i])

	for server, vars in enumerate(vmAssignment):
		AtMost(vars, servers[server]) # at most k variables per server, with k=servers[server], i.e., server capacity

	sol = Solver().solve(expression)

	print("Servers:", servers[:nServers])

	if sol.success:
		print("Results:")
		for iJob, job in enumerate(variables):
			vmAssign = []
			for vm in job:
				res = 0
				for i, server in enumerate(vm):
					if sol[server]:
						res = i
						break
				vmAssign.append(res)
			print('Job ' + str(iJob) + ":", vmAssign)

		nServers -= 1
		'''
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
		'''

	else:
		print('No solution found with', nServers, 'servers')
		break

