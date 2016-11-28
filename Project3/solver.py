sat = True
unsat = False

import sys
from pymzn import *

class Solver:
	def __init__(self):
		self.res = None
		self.f = open("tmp.dzn", "w")

	def putInt(self, name, v):
		self.f.write("%s = %d;\n" % (name, v))

	def putList(self, name, l):
		self.f.write("%s = [" % name)
		self.f.write(", ".join([str(i) for i in l]))
		self.f.write("];\n")

	def check(self):
		try:
			self.f.close()
			self.res = minizinc("problem.mzn", "tmp.dzn")[0]
			return sat
		except MiniZincUnsatisfiableError as e:
			return unsat

	def model(self):
		return self.res
