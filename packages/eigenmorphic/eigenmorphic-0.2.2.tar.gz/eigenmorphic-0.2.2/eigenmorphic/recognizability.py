from sage.modules.free_module_element import vector
from sage.matrix.constructor import matrix
from sage.rings.integer_ring import ZZ

def is_periodic_morphic (t, s, getp=False, verb=False):
	"""
	Test if the shift of the directive sequence t*s^oo is periodic.
	Return the period if periodic, otherwise return None.
	"""
	from sage.combinat.words.morphism import WordMorphism
	from eigenmorphic.coboundary import return_substitution
	seen = set()
	while s not in seen:
		if verb > 0:
			print(s)
		seen.add(s)
		s,rw = return_substitution(s, getrw=True, verb=verb-2)
		dt = dict()
		for w in rw:
			dt[rw[w]] = t(w)
		t = WordMorphism(dt)
		it = list(set(t.images()))
		if verb > 1:
			print("rw = %s" % rw)
			print("it = %s" % it)
		if len(it) == 1:
			break
	if len(it) == 1:
		return it[0]
	return None

def is_recognizable(t, s, nmin=3, nmax=100, pas=5, verb=False):
	"""
	Test if t is recognizable in the subshift of s.

	INPUT:

		- ``t`` - WordMorphism
		
		- ``s`` - WordMorphism

		- ``nmin`` - int (default: ``3``)

		- ``nmax`` - int (default: ``100``)

		- ``pas`` - int (default: ``5``)

		- ``verb`` - bool (default: ``False``)

	OUTPUT:
		A bool.

	EXAMPLES:

		sage: from eigenmorphic.recognizability import is_recognizable
		sage: t = WordMorphism('a->0,b->0,c->1')
		sage: s = WordMorphism('a->ab,b->ac,c->a')
		sage: is_recognizable(t,s)
		True

	"""
	from sage.matrix.special import identity_matrix
	from sage.functions.other import floor
	for n in range(nmin,nmax,pas):
		if verb > 0:
			print("n = %s" % n)
		# find length of intervals
		k = floor(n/2) # index of the letter we want to be recognized
		v0 = vector([1 for _ in t.codomain().alphabet()])
		m = t.incidence_matrix()
		L = s.language(n)
		Id = identity_matrix(n)
		if verb > 1:
			print("v0 = %s" % v0)
			print("L = %s" % L)
		ml = min([v0*m*vector(w[:k].abelian_vector()) for w in L])
		Ml = ml + min([v0*m*vector(w[k+1:].abelian_vector()) for w in L])+1
		if verb > 2:
			print("ml = %s, Ml = %s" % (ml, Ml))
		# make dictionnary of words with same image by t
		d = dict()
		for w in L:
			w2 = t(w)
			K = v0*m*vector(w[k:k+1].abelian_vector()) # length of image of letter w[k]
			dec = v0*m*vector(w[:k].abelian_vector()) - ml
			if verb > 2:
				print("w2 = %s" % w2)
			for i in range(dec, dec+K):
				w3 = w2[i:i+Ml]
				if verb > 2:
					print(w3)
				if w3 not in d:
					d[w3] = []
				d[w3].append((w,i-dec))
		if verb > 1:
			print(d)
		for w2 in d:
			if len(d[w2]) != 1:
				if verb > 0:
					print("%s :" % w2)
					for _ in d[w2]:
						print(_)
				if len({(w3[k],i) for w3,i in d[w2]}) != 1:
					break
		else:
			return True
	#return False
	raise RuntimeError("Sorry, I was not able to check recognizability. Try with bigger nmax.")

def is_periodic (s, m0=None, check_primitive=True, getp=False, verb=False):
	"""
	Test if the shift of the substitution s is periodic.

	INPUT:

		- ``s`` - WordMorphism

		- ``m0`` - matrix (default: ``None``)

		- ``check_primitive`` - bool (default: ``True``) -- if True, check primitivity

		- ``getp`` - bool (default: ``False``) -- if True, return the period

		- ``verb`` - int (default: ``False``) -- if >0, print informations.

	OUTPUT:
		A boolean, or an int if getp is True

	EXAMPLES:

		sage: from eigenmorphic.recognizability import is_periodic
		sage: is_periodic(WordMorphism('a->ab,b->ba'))
		False
		sage: is_periodic(WordMorphism('a->ab,b->ab'))
		True
		sage: is_periodic(WordMorphism('a->bc,b->ab,c->ca'))
		True

	"""
	from eigenmorphic.coboundary import return_substitution
	if check_primitive:
		if not s.is_primitive():
			raise ValueError("The input substitution must be primitive !")
	if m0 is None:
		from sage.matrix.special import identity_matrix
		m0 = identity_matrix(len(s.domain().alphabet()))
	b = max(m0.eigenvalues())[0]
	if b.minpoly().degree() != 1:
		return False
	seen = set()
	if getp:
		vl = vector([1 for _ in s.domain().alphabet()])*m0 # vector of lengths
	while s not in seen:
		if verb > 0:
			print(s)
		seen.add(s)
		if getp:
			s,rw = return_substitution(s, check_primitive=False, getrw=True, verb=verb-2)
			if verb > 1:
				print(rw)
			vl *= rw_to_matrix(rw)
			if verb > 1:
				print(vl)
			if len(vl) == 1:
				break
		else:
			s = return_substitution(s, check_primitive=False, verb=verb-1)
	if getp:
		if len(set(s(0))) == 1:
			return sum(vl)
		return None
	return len(s.domain().alphabet()) == 1

def rw_to_matrix (rw):
	"""
	Used by is_periodic.
	"""
	l = list(rw.keys())
	l.sort(key=lambda x:rw[x])
	return matrix([w.abelian_vector() for w in l]).transpose()

