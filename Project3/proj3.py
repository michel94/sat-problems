#!/usr/bin/python3

from random import shuffle
from solver import *

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

def randomSolution(jobs, servers):
	jobs = jobs + []
	iServers = servers
	nExec = 1000
	minServers = len(iServers)
	backupServers = [[i[0], i[1]] for i in minServerList(iServers, len(iServers))]

	for _ in range(nExec):
		servers = [[i[0], i[1]] for i in backupServers]
		shuffle(jobs)
		restart = False

		best = 0
		for j in jobs:
			col = set()
			for vm in j:
				ok = False
				for s in range(len(servers)):
					if (not vm[2] or s not in col) and vm[0] <= servers[s][0] and vm[1] <= servers[s][1]:
						col.add(s)
						best = max(best, s+1)
						servers[s][0] -= vm[0]
						servers[s][1] -= vm[1]
						ok = True
						break
				
				if not ok:
					restart = True
			if restart:
				break
		if not restart:
			minServers = min(minServers, best)

	return minServers

f = None
solverPath = None
VERBOSE = False
if len(sys.argv) < 2:
	print("Usage: ./proj3.py input.txt flags")
	exit(0)
else:
	for arg in sys.argv:
		if arg.startswith("--"):
			arg = arg[2:]
			if arg == 'verbose':
				VERBOSE = True
			elif arg.startswith("solver="):
				solverPath = arg[7:]
		else:
			f = open(arg, "r")
			

if f == None:
	print('No test instance provided')
	exit(1)

nServers = int(f.readline())
allServers = [0] * nServers
for i in range(nServers):
	s = [int(i) for i in f.readline().split()]
	allServers[s[0]] = (s[1], s[2], s[0])

nVMs = int(f.readline())

totalRes1 = 0
totalRes2 = 0
jobId = 0
jobs = []
jobRes = [0,0]
for i in range(nVMs):
	s = f.readline().split()
	job = [int(i) for i in s[:-1]]
	if job[0] >= len(jobs):
		jobs.append([])

	totalRes1 += job[2]
	totalRes2 += job[3]
	res = job[2:]
	if s[-1] == 'False':
		res.append(False)
	else:
		res.append(True)
	res.append(jobId)
	jobId += 1

	jobs[job[0]].append(res)

for j in jobs:
	jobRes[0] = max(jobRes[0], sum([i[0] for i in j]))
	jobRes[1] = max(jobRes[1], sum([i[1] for i in j]))


if solverPath == None:
	if nVMs * nServers < 3000:
		solverPath = "mzn-g12mip"
	else:
		solverPath = "mzn-gecode"
if VERBOSE and solverPath != None:
	print("==== Using %s solver ====" % solverPath)

def sortKey(t):
	return not t[2]

nJobs = 0
startIndex = []
endIndex = []
size = 1

res1Vms = []
res2Vms = []
res1Server = []
res2Server = []

for j in jobs:

	j.sort(key=sortKey)
	i = 0
	while i < len(j) and j[i][2] != False:
		i+=1
	i-=1

	if i > 1:
		nJobs += 1
		startIndex.append(size)
		endIndex.append(size+i)
	
	for i in j:
		res1Vms.append(i[0])
		res2Vms.append(i[1])

	size += len(j)

for s in allServers:
	res1Server.append(s[0])
	res2Server.append(s[1])

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
	LB = max(LB, sum([i[2] for i in j]))


if VERBOSE:
	print('==== Computing upper bound ====')

UB = nServers
tries = 10
while LB + 2 < UB and tries > 0:
	UB = min(UB, randomSolution(jobs, allServers)) # Greedy upper bound
	tries -= 1

servers = minServerList(allServers, UB)
nServers = len(servers)

if VERBOSE:
	print('==== Solving with %d servers, using a list of %d ====' % (LB, nServers))

res1Server = [i[0] for i in servers]
res2Server = [i[1] for i in servers]

solver = Solver(solverPath)
solver.putInt('nServers', nServers)
solver.putInt('nVms', nVMs)
solver.putInt('nJobs', nJobs)
solver.putInt('LB', LB)
solver.putInt('UB', UB)
solver.putList('res1Vms', res1Vms)
solver.putList('res2Vms', res2Vms)
solver.putList('res1Server', res1Server)
solver.putList('res2Server', res2Server)
solver.putList('jobStart', startIndex)
solver.putList('jobEnd', endIndex)

if solver.check() == sat:
	model = solver.model()
	vms = model['vmAssignment']
	usedServers = model['servers']
	assign = [0] * nVMs
	print("o " + str(len(usedServers)))
	id = 0
	for j in jobs:
		for v in j:
			assign[id] = vms[v[3]] - 1
			id += 1
	
	id = 0
	for j, job in enumerate(jobs):
		for v, vm in enumerate(job):
			print("%d %d -> %d" % (j, v, servers[assign[id]][2] ))
			id += 1

else:
	print('UNSAT')

