#!/usr/bin/python3

from math import *
import sys

from formula import *
from encoding import *

def nextCore(l, cores):
	l.sort()
	l.reverse()

	q = [l[0]]
	cores.append(l[0])
	del l[0]
	
	while len(q) > 0:
		cur = q[0]
		del q[0]

		i = 0
		while i<len(l):
			if cur[0] < l[i][0] or cur[1] < l[i][1]:
				q.append(l[i])
				cores.append(l[i])
				del l[i]
			else:
				i+=1

def minServerList(servers, needed):
	cores = []
	l = list(servers)
	while len(cores) < needed:
		nextCore(l, cores)

	return cores

class Result:
	def __init__(self, nServers, sol, variables, servers):
		self.nServers = nServers
		self.sol = sol
		self.variables = variables
		self.servers = servers

	def pretty(self):
		print("Solution found with", self.nServers, "servers")
		print("Results:")
		for iJob, job in enumerate(self.variables):
			vmAssign = []
			for vm in job:
				res = 0
				for i, server in enumerate(vm):
					if self.sol[server]:
						res = i
						break
				vmAssign.append(res)
			print('Job ' + str(iJob) + ":", vmAssign)

		print("Servers used:", [self.sol[v] for v in self.servers])

	def __str__(self):
		text = []
		text.append('o ' + str(self.nServers))
		for iJob, job in enumerate(self.variables):
			for iVm, vm in enumerate(job):
				for iServer, server in enumerate(vm):
					if self.sol[server]:
						text.append("%d %d -> %d" % (iJob, iVm, iServer) )

		return "\n".join(text)

nServers = int(input())
servers = [0] * nServers
for i in range(nServers):
	s = [int(i) for i in input().split()]
	servers[s[0]] = (s[1], s[2])

servers = sorted(servers)
servers.reverse()

nVMs = int(input())
jobs = []
vmResources = []
totalRes1 = 0
totalRes2 = 0
for i in range(nVMs):
	s = input().split()
	job = [int(i) for i in s[:-1]]
	if job[0] >= len(jobs):
		jobs.append([])
	vmResources.append(job[2:])
	totalRes1 += job[2]
	totalRes2 += job[3]
	if s[-1] == 'False':
		jobs[job[0]].append(False)
	else:
		jobs[job[0]].append(True)


res1 = [i[0] for i in servers]
res2 = [i[1] for i in servers]
res1 = sorted(res1)
res1.reverse()
res2 = sorted(res2)
res2.reverse()

maxRes1 = [0] * nServers
maxRes2 = [0] * nServers
maxRes1[0] = res1[0]
maxRes2[0] = res2[0]
for i in range(1, nServers):
	maxRes1[i] = maxRes1[i-1] + res1[i]
	maxRes2[i] = maxRes2[i-1] + res2[i]

'''
print(res1)
print(maxRes1)
print(res2)
print(maxRes2)
print(totalRes1, totalRes2)'''


LB = 1
i = nServers-1
while i>=0 and maxRes1[i] >= totalRes1 and maxRes2[i] >= totalRes2:
	LB = i+1
	i-=1

solutionFound = False
best = None

maxServers = nServers
while maxServers >= LB:
	#sys.stdout.write('==== Trying using %d servers ==== \r' % (maxServers) )
	expression = Formula()

	variables = [[[Var("VM" + str(job) + "-" + str(vm) + "-" + str(server) ) for server in range(nServers)] for vm in range(len(jobs[job]))] for job in range(len(jobs))]
	serverUsed = [Var("Server" + str(server)) for server in range(len(servers))]

	vmAssignment = [[] for i in range(nServers)] # encoding of assignment of servers to vm, only one variable per server can be set to true

	for iJob, job in enumerate(variables):
		for vm in job:
			expression &= ExactlyOnce(vm)
			for i, v in enumerate(vm):
				expression &= (-v | serverUsed[i])
			for i in range(len(vm)):
				vmAssignment[i].append(vm[i])


		collocation = jobs[iJob]
		exclude = []
		indexes = []
		for i in range(len(collocation)):
			if collocation[i]:
				indexes.append(i)
				exclude.append(job[i])

		for i in range(len(exclude)):
			for j in range(i+1, len(exclude)):
				for s in range(nServers):
					expression &= (-exclude[i][s] | -exclude[j][s])


	for server, vars in enumerate(vmAssignment):
		expression &= WeightedAtMost(vars, [r[0] for r in vmResources], servers[server][0])
		expression &= WeightedAtMost(vars, [r[1] for r in vmResources], servers[server][1])

	expression &= AtMost(serverUsed, maxServers)

	sol = Solver("minisat").solve(expression, verbose=False)
	sys.stdout.write('\r\r\r')
	#print("Servers:", servers[:nServers])

	if sol.success:
		solutionFound = True
		best = Result(maxServers, sol, variables, serverUsed)

		maxServers -= 1
		
	else:
		break

if solutionFound:
	#print()
	#best.pretty()
	print(best)
else:
	print("No solution found")

