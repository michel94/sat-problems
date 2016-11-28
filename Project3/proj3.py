#!/usr/bin/python3

from random import shuffle
from solver import *

f = None
PRETTY_OUTPUT = False
if len(sys.argv) < 2:
	print("Usage: ./proj3.py input.txt flags")
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

jobId = 0
jobs = []
for i in range(nVMs):
	s = f.readline().split()
	job = [int(i) for i in s[:-1]]
	if job[0] >= len(jobs):
		jobs.append([])

	res = job[2:]
	if s[-1] == 'False':
		res.append(False)
	else:
		res.append(True)
	res.append(jobId)
	jobId += 1

	jobs[job[0]].append(res)


s = Solver()

def sortKey(t):
	return not t[2]

nJobs = 0
startIndex = []
endIndex = []
size = 1

res1 = []
res2 = []
res1Server = []
res2Server = []

for j in jobs:

	j.sort(key=sortKey)
	i = 0
	while i < len(j) and j[i][2] != False:
		i+=1
	i-=1

	if i > 0:
		nJobs += 1
		startIndex.append(size)
		endIndex.append(size+i)
	
	for i in j:
		res1.append(i[0])
		res2.append(i[1])

	size += len(j)

for s in allServers:
	res1Server.append(s[0])
	res2Server.append(s[1])


solver = Solver()
solver.putInt('nServers', nServers)
solver.putInt('nVms', nVMs)
solver.putInt('nJobs', nJobs)
solver.putList('res1Vms', res1)
solver.putList('res2Vms', res2)
solver.putList('res1Server', res1Server)
solver.putList('res2Server', res2Server)
solver.putList('jobStart', startIndex)
solver.putList('jobEnd', endIndex)
if solver.check() == sat:
	model = solver.model()
	vms = model['vmAssignment']
	servers = model['servers']
	assign = [0] * nVMs
	print("o " + str(len(servers)))
	id = 0
	for j in jobs:
		for v in j:
			assign[id] = vms[v[3]] - 1
			id += 1
	
	id = 0
	for j, job in enumerate(jobs):
		for v, vm in enumerate(job):
			print("%d %d -> %d" % (j, v, assign[id]))
			id += 1
