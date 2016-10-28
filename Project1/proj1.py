#!/usr/bin/python3

from math import *
import time
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
	def __init__(self, nServers, sol, variables, serversVars, servers):
		self.nServers = nServers
		self.sol = sol
		self.variables = variables
		self.serversVars = serversVars
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
						res = self.servers[i][2]
						break
				vmAssign.append(res)
			print('Job ' + str(iJob) + ":", ", ".join([str(i) for i in vmAssign]) )

		print("Servers used:", self.servers)

	def __str__(self):
		text = []
		text.append('o ' + str(self.nServers))
		for iJob, job in enumerate(self.variables):
			for iVm, vm in enumerate(job):
				for iServer, server in enumerate(vm):
					if self.sol[server]:
						text.append("%d %d -> %d" % (iJob, iVm, self.servers[iServer][2]) )

		return "\n".join(text)

f = None
PRETTY_OUTPUT = False
if len(sys.argv) < 2:
	print("Usage: ./proj1.py input.txt flags")
	exit(0)
else:
	f = open(sys.argv[1], "r")
	if len(sys.argv) > 2:
		if sys.argv[2] == '--verbose':
			PRETTY_OUTPUT = True

nServers = int(f.readline())
allServers = [0] * nServers
for i in range(nServers):
	s = [int(i) for i in f.readline().split()]
	allServers[s[0]] = (s[1], s[2], s[0])

nVMs = int(f.readline())
jobs = []
vmResources = []
totalRes1 = 0
totalRes2 = 0
for i in range(nVMs):
	s = f.readline().split()
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


res1 = [i[0] for i in allServers]
res2 = [i[1] for i in allServers]
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

LB = 1
i = nServers-1
while i>=0 and maxRes1[i] >= totalRes1 and maxRes2[i] >= totalRes2:
	LB = i+1
	i-=1

for j in jobs:
	LB = max(LB, sum(j))

if PRETTY_OUTPUT:
	print('Lower bound:', LB)

solutionFound = False
best = None

maxServers = nServers
servers = minServerList(allServers, maxServers)
while maxServers >= LB:
	
	if PRETTY_OUTPUT:
		print('==== Trying with %d servers, using a list of %d ====' % (maxServers, nServers))
	expression = Formula()

	variables = [[[Var("VM" + str(job) + "-" + str(vm) + "-" + str(server) ) for server in range(nServers)] for vm in range(len(jobs[job]))] for job in range(len(jobs))]
	serversUsed = [Var("Server" + str(server)) for server in range(nServers)]

	vmAssignment = [[] for i in range(nServers)] # encoding of assignment of servers to vm, only one variable per server can be set to true
	for iJob, job in enumerate(variables):
		for vm in job:
			expression &= ExactlyOnce(vm)
			for i, v in enumerate(vm):
				expression &= (-v | serversUsed[i])
			for i in range(len(vm)):
				vmAssignment[i].append(vm[i])


		collocation = jobs[iJob]
		exclude = []
		for i in range(len(collocation)):
			if collocation[i]:
				exclude.append(job[i])

		for i in range(len(exclude)):
			for j in range(i+1, len(exclude)):
				for s in range(nServers):
					expression &= (-exclude[i][s] | -exclude[j][s])

	if PRETTY_OUTPUT:
		print('Encoding cardinality')
	for server, vars in enumerate(vmAssignment):
		if PRETTY_OUTPUT:
			print('server', server)
		expression &= WeightedAtMost(vars, [r[0] for r in vmResources], servers[server][0])
		expression &= WeightedAtMost(vars, [r[1] for r in vmResources], servers[server][1])
	
	expression &= AtMost(serversUsed, maxServers)
	
	sol = Solver("minisat").solve(expression, verbose=PRETTY_OUTPUT)

	if sol.success:
		
		solutionFound = True
		cntServers = sum([sol[s] for s in serversUsed])
		best = Result(cntServers, sol, variables, serversUsed, servers)
		
		maxServers = min(maxServers, cntServers) - 1
		servers = minServerList(allServers, maxServers)
		nServers = len(servers)
	else:
		break

if solutionFound:
	if PRETTY_OUTPUT:
		print()
		best.pretty()
	else:
		print(best)
else:
	print("No solution found")

