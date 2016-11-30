#!/usr/bin/python3

from z3 import *
from random import shuffle

def sumPerServer(vms, weights, server, serverRes, serverCount):
	l1 = [If(vms[i] == server, weights[i][0], 0) for i in range(len(vms))]
	l2 = [If(vms[i] == server, weights[i][1], 0) for i in range(len(vms))]
	clauses = [Implies(Or([v == server for v in vms]), serverCount)]
	t = simplify(sum(l1))
	
	clauses.extend([simplify(t <= serverRes[0]), simplify(sum(l2) <= serverRes[1])])
	return clauses


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

def MySolver():
	return Then('simplify', 'elim01', 'propagate-ineqs', 'elim-term-ite', 'qflia', 'smt').solver()
	
def setupSolver(servers, nServers, maxServers, serverCount):
	s = MySolver()
	if PRETTY_OUTPUT:
		print('==== Trying with %d servers, using a list of %d ====' % (maxServers, nServers))

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

	for server in range(nServers):
		clauses = sumPerServer(vms, vmResources, server, servers[server], serverCount[server])
		s.append(clauses)
	
	dct = {}
	for i in range(len(servers)):
		dct[servers[i][2]] = i

	s.push()
	if nServers != maxServers:
		s.add( simplify(sum([If(cnt, 0, 1) for cnt in serverCount]) <= maxServers) )
	
	return s


def randomSolution(jobs, servers):
	jobs = jobs + []
	iServers = servers
	nExec = 10000
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

def ascendingSearch(LB, allServers):
	global solution
	maxServers = LB
	servers = minServerList(allServers, maxServers)
	nServers = len(servers)

	best = None
	while maxServers <= len(allServers):
		serverCount = [Bool("S" + str(i)) for i in range(nServers)]
		s = setupSolver(servers, nServers, maxServers, serverCount)

		if s.check() == sat:
			best = s.model()
			solution[0] = maxServers
			solution[1] = servers + []
			break
		else:
			maxServers += 1
			servers = minServerList(allServers, maxServers)
			nServers = len(servers)
			if PRETTY_OUTPUT:
				print('No solution found')

	return best

def descendingSearch(LB, allServers):
	global solution

	maxServers = randomSolution(problem, allServers) # Greedy upper bound
	servers = minServerList(allServers, maxServers)
	nServers = len(servers)
	
	best = None
	createSolver = True
	s = None
	while maxServers >= LB:
		serverCount = [Bool("S" + str(i)) for i in range(nServers)]
		if createSolver:
			createSolver = False
			s = setupSolver(servers, nServers, maxServers, serverCount)
		else:
			if PRETTY_OUTPUT:
				print('==== Trying with %d servers, keeping a list of %d ====' % (maxServers, nServers))
			s.pop(1)
			s.push()
			s.add( simplify(sum([If(cnt, 0, 1) for cnt in serverCount]) <= maxServers) )
			
		if s.check() == sat:
			best = s.model()
			solution[0] = maxServers
			solution[1] = servers + []
			
			cntServers = sum([is_true(best[server]) for server in serverCount])
			maxServers = min(maxServers, cntServers) - 1
			servers = minServerList(allServers, maxServers)
			if len(servers) < nServers:
				createSolver = True
			nServers = len(servers)

		else:
			if PRETTY_OUTPUT:
				print('Solution not found for %d servers' % maxServers)
			break

	return best

f = None
PRETTY_OUTPUT = False
if len(sys.argv) < 2:
	print("Usage: ./proj2.py input.txt flags")
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
problem = []
for i in range(nVMs):
	s = f.readline().split()
	job = [int(i) for i in s[:-1]]
	if job[0] >= len(jobs):
		jobs.append([])
		problem.append([])
	vmResources.append(job[2:])
	totalRes1 += job[2]
	totalRes2 += job[3]
	if s[-1] == 'False':
		jobs[job[0]].append(False)
		problem[job[0]].append(job[2:] + [False])

	else:
		jobs[job[0]].append(True)
		problem[job[0]].append(job[2:] + [True])


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

variables = [[Int("VM" + str(job) + "-" + str(vm) ) for vm in range(len(jobs[job]))] for job in range(len(jobs))]

solution = [None, None]

set_option(relevancy=10)
#set_option(verbose=10)
#describe_tactics()
#describe_probes()
best = ascendingSearch(LB, allServers)
#best = descendingSearch(LB, allServers)

maxServers = solution[0]
bestServers = solution[1]

if best != None:
	print('o %d' % (maxServers))
	for j, job in enumerate(variables):
			for v, vm in enumerate(job):
				s = best[vm].as_long()
				print("%d %d -> %d" % (j, v, bestServers[s][2] ) )

