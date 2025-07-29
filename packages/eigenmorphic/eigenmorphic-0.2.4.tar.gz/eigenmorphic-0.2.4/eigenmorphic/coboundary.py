from sage.modules.free_module_element import vector
#from sage.matrix.constructor import matrix
from sage.rings.integer_ring import ZZ

def coboundary_basis (s, algo=1, verb=False):
	"""
	Return a basis of the space of coboundaries, as a matrix.
	A coboundary is a linear form such that image of ab(w) is zero
	for every w such that w.w_0 is a word of the language of s.

	INPUT:

		- ``s`` - WordMorphism

		- ``algo`` - int (default: ``1``) - algorithm used

		- ``verb`` - Boolean (default: ``False``) if True print informations.

	OUTPUT:
		A matrix

	EXAMPLES:

		sage: from eigenmorphic import *
		sage: s = WordMorphism('a->ab,b->a')
		sage: coboundary_basis(s)
		[]

		sage: s = WordMorphism('a->b,b->cd,c->ab,d->c')
		sage: coboundary_basis(s)
		[ 1 -1  1 -1]
		[ 0  1 -1  0]

	"""
	if algo == 1:
		n,l = coboundary_graph2(s, verb-1)
		if verb > 0:
			print(n,l)
		return graph_basis(n,l)	
	else:
		_,lr = return_substitution(s, getrw=True)
		if verb > 0:
			print("return words : %s" % list(lr))
		return matrix(matrix([w.abelian_vector() for w in lr]).transpose().kernel().basis())

def coboundary_graph (s, use_badic=None):
	"""
	Return the coboundary graph.
	That is the greatest invariant graph with letters apparing once in edges.

	INPUT:

		- ``s`` - WordMorphism

		- ``use_badic`` - bool (default: ``None``) - if True, return a DetAutomaton (the package badic must be installed).
						If ``None``, try to load the package badic. 

	OUTPUT:
		A DetAutomaton or DiGraph.

	EXAMPLES::

		sage: from eigenmorphic import *
		sage: s = WordMorphism('0->527,1->520,2->0,3->1,4->361,5->461,6->4,7->5')
		sage: coboundary_graph(s)
		DetAutomaton with 2 states and an alphabet of 8 letters

	"""
	if use_badic is None:
		try:
			from badic.cautomata import DetAutomaton
			use_badic = True
		except:
			use_badic = False
	elif use_badic:
		from badic.cautomata import DetAutomaton
	n, l = coboundary_graph2(s)
	R = []
	A = s.domain().alphabet()
	for i in range(len(l)//2):
		if use_badic:
			R.append((l[2*i],A[i],l[2*i+1]))
		else:
			R.append((l[2*i],l[2*i+1],A[i]))
	if use_badic:
		return DetAutomaton(R, avoidDiGraph=True, keep_S=False)
	else:
		return DiGraph(R, multiedges=True, loops=True)

def coboundary_graph2 (s, verb=0):
	r"""
	Compute the coboundary graph of s.
	The result is given as (n,l) where n is the number of vertices,
	and the edge associated to letter of index i is (l[2*i], l[2*i+1]).

	INPUT:

		- ``s`` - a WordMorphism

		- ``verb`` - int (default: ``0``) - if > 0, print informations

	OUTPUT:
		A couple (n, l), with n number of vertices and where (l[2*i], l[2*i+1]) are edges

	EXAMPLES::

		sage: from eigenmorphic.coboundary import coboundary_graph2
		sage: s = WordMorphism('0->527,1->520,2->0,3->1,4->361,5->461,6->4,7->5')
		sage: coboundary_graph2(s)
		(2, [0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0])

	"""
	from sage.combinat.words.morphism import WordMorphism
	A = s.domain().alphabet()
	dA = dict()
	for i,a in enumerate(A):
		dA[a] = i
	s = WordMorphism({i:[dA[a] for a in s(A[i])] for i in range(len(A))})
	n = len(A)
	p = list(range(2*n)) # partition (give vertices from initial vertices)
	f = [] # function that maps initial vertices to initial vertices image by s
	df = dict() # dictionnary that maps vertices to initial vertices image by s
	lsucc = [set() for _ in range(n)]
	nc = 2*n # number of connected component
	for i in range(n):
		w = s(i)
		f.append(w[0]*2)
		f.append(w[-1]*2+1)
		for j in range(len(w)-1):
			lsucc[w[j]].add(w[j+1])

	def connect (i,j):
		if p[i] != p[j]:
			# update p
			m = min(p[i], p[j])
			M = max(p[i], p[j])
			for k in range(2*n):
				if p[k] == M:
					p[k] = m
			return True
		return False

	for i,succ in enumerate(lsucc):
		# connect 2*i+1 with elements of succ
		for j in succ:
			if connect(2*i+1, 2*j):
				nc -= 1
	if verb > 0:
		print(p)
	to_see = list(set(p)) # list of connected component to consider
	while len(to_see) > 0:
		c = to_see.pop()
		rpf = None
		for i in range(2*n):
			if p[i] == c:
				pf = p[f[i]]
				if rpf is not None:
					if connect(rfi, f[i]):
						nc -= 1
						to_see.append(min(rpf, pf))
				rpf = pf
				rfi = f[i]
	# relabel with numbers from 0 to len-1
	sp = list(set(p))
	p = [sp.index(i) for i in p]
	return nc, p

def graph_basis (n, l):
	r"""
	Return a basis of the set of differences from the graph with n vertices
	given as edges (l[2*i], l[2*i+1]).

	INPUT:

		- ``n`` - int - number of vertices

		- ``l`` - list such that (l[2*i], l[2*i+1]) are edges

	OUTPUT:
		A basis of the coboundary space, given as a matrix.

	EXAMPLES::

		sage: from eigenmorphic import *
		sage: graph_basis(2, [0,1,1,0,1,1])
		[ 1 -1  0]

	"""
	from sage.modules.free_module_element import zero_vector
	from sage.matrix.special import identity_matrix
	e = [zero_vector(n-1)]+list(identity_matrix(n-1))
	c = []
	for a in range(len(l)//2):
		c.append(e[l[2*a+1]] - e[l[2*a]])
	return matrix(c).transpose()

def return_substitution (s, check_primitive=True, getrw=False, verb=False):
	"""
	Return the set of return words on some letter.

	INPUT:

		- ``s`` - WordMorphism

		- ``check_primitive`` - bool (default: ``True``) - if True, check that the substitution is primitive

		- ``getrw`` - bool (default: ``False``) - if True, return also the set of return words

		- ``verb`` - bool (default: ``False``) - if True print informations.

	OUTPUT:
		A substitution.

	EXAMPLES:

		sage: from eigenmorphic import *
		sage: s = WordMorphism('a->ab,b->a')
		sage: return_substitution(s, getrw=True)
		(WordMorphism: 0->01, 1->0, {word: a: 1, word: ab: 0})

	"""
	from sage.combinat.words.morphism import WordMorphism
	if check_primitive:
		if not s.is_primitive():
			raise ValueError("The input substitution must be primitive !")
	rw = dict() # set of return words
	rs = dict() # result substitution
	to_see = [] # set of words to consider
	# take a word u in the subshift
	s0 = s
	n = 0
	while True:
		l = s.fixed_points()
		if len(l) > 0:
			break
		s = s*s0
		n += 1
	if verb > 0:
		print("take the %s-th power of s" % (n+1))
	u = l[0]
	if verb > 1:
		print("chosen fixed point: %s" % u)
	# find a first return word
	for i,a in enumerate(u):
		if i > 0 and a == u[0]:
			to_see.append(u[:i])
			rw[u[:i]] = 0
			rs[0] = []
			break
	if verb > 0:
		print("first return word found: %s" % u[:i])
	def add(w):
		if w not in rw:
			to_see.append(w) # do the same for every new return word
			rs[len(rw)] = []
			rw[w] = len(rw)
	while len(to_see) > 0:
		w = to_see.pop()
		# compute the image by s and decompose it as return words
		sw = s(w)
		ri = 0
		for i,a in enumerate(sw):
			if i > 0 and a == sw[0]:
				w2 = sw[ri:i]
				add(w2)
				rs[rw[w]].append(rw[w2])
				ri = i
		w2 = sw[ri:]
		add(w2)
		rs[rw[w]].append(rw[w2])
	if getrw:
		return WordMorphism(rs), rw
	return WordMorphism(rs)

