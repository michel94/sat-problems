#!/usr/bin/python2

from z3 import *

def sumPerServer(vms, weights, server, serverRes, serverCount):
	l1 = [If(vms[i] == server, 1, 0) * weights[i][0] for i in range(len(vms))]
	l2 = [If(vms[i] == server, 1, 0) * weights[i][1] for i in range(len(vms))]
	
	t = sum(l1)
	return [t <= serverRes[0], sum(l2) <= serverRes[1], (t>0) == serverCount]

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

nServers = LB
maxServers = nServers
servers = minServerList(allServers, maxServers)

variables = [[Int("VM" + str(job) + "-" + str(vm) ) for vm in range(len(jobs[job]))] for job in range(len(jobs))]

best = None
bestServers = []

while maxServers <= len(allServers):
	s = Solver()
	print('==== Trying with %d servers, using a list of %d ====' % (maxServers, nServers))
	serverCount = [Bool("S" + str(i)) for i in range(nServers)]

	vms = []
	for j in range(len(variables)):
		job = variables[j]
		vms.extend(job)
		d = []
		for v, vm in enumerate(job):
			s.add(vm >= 0)
			s.add(vm < nServers)
			if jobs[j][v]:
				d.append(vm)

		if len(d) > 1:
			s.add(Distinct(d))

	s.add( sum([If(cnt, 0, 1) for cnt in serverCount]) <= maxServers )
	for server in range(nServers):
		clauses = sumPerServer(vms, vmResources, server, servers[server], serverCount[server])
		s.append(clauses)
		

	print('Solving...')
	if s.check() == sat:
		best = s.model()
		bestServers = servers
		break
		'''
		cntServers = sum([is_true(best[s]) for s in serverCount])
		maxServers = min(maxServers, cntServers) + 1
		servers = minServerList(allServers, maxServers)
		nServers = len(servers)
		'''
	else:
		maxServers += 1
		servers = minServerList(allServers, maxServers)
		nServers = len(servers)
		print('No solution found')
		

if best != None:
	print('o %d' % (maxServers))
	for j, job in enumerate(variables):
			for v, vm in enumerate(job):
				s = best[vm].as_long()
				print("%d %d -> %d" % (j, v, bestServers[s][2] ) )


