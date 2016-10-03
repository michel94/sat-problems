d = {}
clauses = 0
vars=0

while True:
	try:
		s = input()
		if len(s) == 0:
			continue
		if s[0] == 'p' or s[0] == 'c':
			print(s)
			continue
		clauses+=1
		s = s.split()
		l = []
		for name in s:
			v = True
			if name[0] == '-':
				v = False
				name = name[1:]
			#print(v, name)
			if name not in d:
				vars+=1
				d[name] = len(d)+1
			if v:
				l.append(str(d[name]))
			else:
				l.append(str(-d[name]))
		l.append('0')
		print(' '.join(l))
	except EOFError as e:
		break

