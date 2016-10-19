import os
import subprocess

class Formula:
	def __init__(self):
		self.clauses = []
		pass
	 # Add clause
	def __iand__(self, right):
		if isinstance(right, Clause):
			self.clauses.append(right)
		elif isinstance(right, Var):
			self.clauses.append(Clause(right))
		elif isinstance(right, Formula):
			self.clauses.extend(right.clauses)
		else:
			raise("Wrong argument type")

		return self
	def __str__(self):
		return str(self.clauses)

class Var:
	def __init__(self, name, generateFalse=True):
		self.name = name
		self.signal = True
		self.false = None
		if generateFalse:
			self.false = Var(name, generateFalse=False)
			self.false.signal = False
			self.false.false = self
	def __ior__(self, right):
		return Clause(right)
	def __or__(self, right):
		c = Clause(self)
		c |= right
		return c
	def __neg__(self):
		return self.false

	def __str__(self):
		if self.signal:
			return self.name
		else:
			return "-" + self.name
	def __repr__(self):
		return str(self)

class Clause:
	def __init__(self, var=None):
		self.vars = []
		if var:
			self.vars.append(var)
	def __ior__(self, right):
		if isinstance(right, Var):
			self.vars.append(right)
		elif isinstance(right, Clause):
			self.vars.extend(right.vars)
		else:
			raise("Wrong argument type")
		return self
	def __or__(self, right):
		if isinstance(right, Var):
			self.vars.append(right)
		elif isinstance(right, Clause):
			self.vars.extend(right.vars)
		else:
			raise("Wrong argument type")
		return self
	def __str__(self):
		return str(self.vars)
	def __repr__(self):
		return str(self.vars)

class Solution:
	def __init__(self, success, vars):
		self.vars = vars
		self.success = success
	def __getitem__(self, var):
		return self.vars[var]

class Solver:
	def __init__(self, solverCmd="minisat"):
		self.solverCmd = solverCmd
	def solve(self, formula, verbose=False):
		d = {}
		rev = {}
		count = 1
		filename = "/tmp/formula.cnf"
		out = open(filename, "w")
		toWrite = []

		for clause in formula.clauses:
			clauseStr = []
			for var in clause.vars:
				if var.name not in d:
					d[var.name] = count
					if var.signal:
						rev[count] = var
					else:
						rev[count] = var.false
					count += 1
			toWrite.append(" ".join([str(d[var.name]) if var.signal else "-" + str(d[var.name]) for var in clause.vars]))
			toWrite.append(" 0\n")
		
		if verbose:
			print("Solving problem with " + str(count-1) + " vars and " + str(len(formula.clauses)) + " clauses using " + self.solverCmd + " solver.")
		
		out.write("p cnf " + str(count-1) + " " + str(len(formula.clauses)) + "\n")
		for s in toWrite:
			out.write(s)
		out.close()

		resFilename = "/tmp/out.cnf"
		null = open(os.devnull, 'w')
		if self.solverCmd.endswith('geling'):
			res  = open(resFilename, 'w')
			stream = subprocess.call([self.solverCmd, filename], stderr=null, stdout=res)
			res = open(resFilename, "r")
			l = res.readlines()
			values = []
			for line in l:
				if line[0] == 's':
					r = line.split()
					if r[1] == 'UNSATISFIABLE':
						return Solution(False, {})
				elif line[0] == 'v':
					values.extend([int(i) for i in line.split()[1:]])

			d = {}
			for i in [int(j) for j in values]:
				if i != 0:
					d[rev[abs(i)]] = i > 0
			return Solution(True, d)
			
		else:
			
			stream = subprocess.call([self.solverCmd, filename, resFilename], stderr=null, stdout=null)
			res = open(resFilename, "r")
			l = res.readlines()
			if len(l) == 0 or l[0].startswith('UNSAT'):
				return Solution(False, {})
			else:
				d = {}
				for i in [int(j) for j in l[1].split()]:
					if i != 0:
						d[rev[abs(i)]] = i > 0
				return Solution(True, d)

