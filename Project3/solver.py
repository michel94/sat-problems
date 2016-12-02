sat = True
unsat = False

import sys, os
import subprocess

class Solver():
	def __init__(self, path=None):
		self.res = None
		self.f = open("data.dzn", "w")
		if path != None:
			self.solverCmd = path
		else:
			self.solverCmd = "mzn-g12mip"

	def putInt(self, name, v):
		self.f.write("%s = %d;\n" % (name, v))

	def putList(self, name, l):
		self.f.write("%s = [" % name)
		self.f.write(", ".join([str(i) for i in l]))
		self.f.write("];\n")

	def check(self):
		self.f.close()

		null = open(os.devnull, 'w')
		resFilename = "result.out"
		res  = open(resFilename, 'w')
		stream = subprocess.call([self.solverCmd, "model.mzn", "data.dzn"], stderr=null, stdout=res)
		res = open(resFilename, "r")
		l = res.readlines()
		#print(l)
		l = [int(i) for i in l[0].split()]
		self.res = {}
		self.res['vmAssignment'] = l
		self.res['servers'] = set(l)
		return sat
		
		#return unsat

	def model(self):
		return self.res

