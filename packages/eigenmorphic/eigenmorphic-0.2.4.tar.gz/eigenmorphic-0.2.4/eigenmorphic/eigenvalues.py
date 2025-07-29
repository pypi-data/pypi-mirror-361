from sage.modules.free_module_element import vector
#from sage.matrix.constructor import matrix
from sage.rings.integer_ring import ZZ
from sage.matrix.special import identity_matrix
from eigenmorphic.coboundary import coboundary_basis
from sage.rings.qqbar import QQbar
from sage.rings.number_field.number_field import NumberField
from sage.graphs.digraph import DiGraph
from sage.combinat.words.morphism import WordMorphism

def strlist(l):
	return ', '.join(map(str, l))

def latlist(l):
	from sage.misc.latex import latex
	return r',\ '.join(map(latex, l))

class ModuleEigenvalues:
	"""
	Set of eigenvalues of a subshift as a Z[1/d]-module of finite rank.
	"""
	def __init__ (self, B, d):
		"""
		Initialize the Z[1/d]-module with a basis B and a denominator d.
		"""
		self.d = d
		self.B = B
		self.b = B[0].parent().gen()

	def __repr__ (self):
		"""
		String representation of the Z[1/d]-module
		"""
		txt = "Z"
		if self.d != 1:
			txt += "[1/%s]" % self.d
		if len(self.B) > 1:
			txt += "*{%s}" % strlist(self.B)
		elif self.B[0] != 1 and self.B[0] != -1:
			txt = ("%s" % self.B[0]) + txt
		if self.b.minpoly().degree() > 1 and (len(self.B) > 1 or self.d not in ZZ):
			txt += "\nwhere %s is root of %s" % (self.b, self.b.minpoly())
		return txt

	def _latex_(self):
		"""
		Latex representation of the Z[1/d]-module
		"""
		from sage.misc.latex import latex
		txt = r"\mathbb{Z}"
		if self.d != 1:
			txt += r"\left[ \frac{1}{%s} \right] " % latex(self.d)
		if len(self.B) > 1:
			txt += r"\left\{ %s \right\}" % latlist(self.B)
		elif self.B[0] != 1 and self.B[0] != -1:
			txt = (r"%s" % latex(self.B[0])) + txt
		if self.b.minpoly().degree() > 1 and (len(self.B) > 1 or self.d not in ZZ):
			txt += r"\text{ where $%s$ is root of } %s" % (latex(self.b), latex(self.b.minpoly()))
		from sage.misc.latex import LatexExpr
		return LatexExpr(txt)
		
class GeneralEigenvalues:
	"""
	Set of eigenvalues of a subshift of the form (W n Delta_m) v,
	where - W is a Q-vector space
		  - Delta_m is the set of rows vectors w such that w m^n
			has integer coordinates for n large enough, where m is a matrix
		  - v is a vector
	"""
	def __init__ (self, m, W, v):
		"""
		Initialize the general set of eigenvalues with a matrix m, a basis of W and a vector v.
		"""
		self.W = W
		self.m = m
		self.mi = pseudo_inverse(m)
		self.v = v
		self.b = v[0].parent().gen()
		self.K = self.b.parent()

	def __repr__ (self):
		"""
		String representation of a general set of eigenvalues.
		"""
		txt = "(intersection of Q.{%s} and the union over n in N of Z^%s mi^n) times (%s)\nwhere " % (strlist(self.W), self.W.ncols(), strlist(self.v))
		if self.K.degree() > 1:
			txt += "%s is root of %s and " % (self.b, self.b.minpoly())
		txt += "mi is the matrix\n%s" % (self.mi)
		return txt

	def _latex_(self):
		"""
		Latex representation of a general set of eigenvalues.
		"""
		from sage.misc.latex import latex
		txt = r"\left( \mathbb{Q} \{%s\} \cap \bigcup_{n \in \mathbb{N}} \mathbb{Z}^%s {%s}^{n} \right) \cdot %s" % (latlist(self.W), latex(self.mi.nrows()), latex(self.mi), latex(matrix([self.v]).transpose()))
		if self.K.degree() > 1:
			txt += r"\text{ where $%s$ is root of } %s" % (latex(self.b), latex(self.b.minpoly()))
		from sage.misc.latex import LatexExpr
		return LatexExpr(txt)
	
	def approxW (self, n, verb=False):
		"""
		Compute (W n Z^A M^-n) v
		"""
		from sage.matrix.special import identity_matrix
		from sage.rings.rational_field import QQ
		Wn = matrix(self.W*(self.m**n), base_ring=QQ).row_space()
		if verb > 0:
			print("Wn = %s" % Wn)
		return identity_matrix(self.m.nrows()).row_space().intersection(Wn)
	
	def approx (self, n, verb=False):
		"""
		Compute a basis of (W n Z^A M^-n) v.
		The set of eigenvalues is the increasing union of such Z-modules for n in N.
		"""
		return simpler_Zmodule(matrix(self.approxW(n, verb=verb).basis())*(self.mi**n)*self.v, verb=verb-1)

def is_pisot(b):
	"""
	Test if an algebraic number is Pisot.
	If b is a WordMorphism, test if its Perron eigenvalue is Pisot.
	"""
	if type(b) == WordMorphism:
		b = max(b.incidence_matrix().eigenvalues())
	pi = b.minpoly()
	np = 0
	for a,_ in pi.roots(ring=QQbar):
		if abs(a) >= 1:
			np += 1
			if np > 1:
				return False
	return True

def pseudo_inverse (m, verb=False):
	"""
	Return the pseudo-inverse of m.
	"""
	from sage.matrix.special import block_diagonal_matrix
	from sage.rings.rational_field import QQ
	from sage.rings.qqbar import QQbar
	J,P = matrix(m, base_ring=QQbar).jordan_form(transformation=True)
	if verb > 0:
		print(J)
		print()
	ls = [0]+J.get_subdivisions()[0]+[J.nrows()]
	if verb > 0:
		print(ls)
	lm = []
	for i in range(len(ls)-1):
		k = ls[i]
		n = ls[i+1]-ls[i]
		ms = J.submatrix(k,k,n,n)
		if ms[0,0] == 0:
			ms = ms.transpose()
		else:
			ms = ms.inverse()
		lm.append(ms)
	mi = block_diagonal_matrix(lm)
	return matrix(P*mi*P.inverse(), base_ring=QQ)

def morphic_eigenvalues(s, t=None, check_recognizable=True, check_periodic=True, simplify=2, verb=False):
	r"""
	Compute eigenvalues of the subshift of the directive sequence t*s^oo.
	It is the subshift generated by t(X_s) where X_s is the subshift of s.
	
	If t is None, compute the set of eigenvalues of the subshift of s.

	INPUT:
		
		- ``s`` - WordMorphism -- a substitution

		- ``t`` - WordMorphism (default: ``None``)
		
		- ``check_recognizability`` - Boolean (default: ``True``) - if True, check if t is recognizable in X_s
		
		- ``check_periodic`` - Boolean (default: ``True``) - if True, check if the subshift is periodic
		
		- ``simplify`` - int (default: ``2``) - Level of simplification.
			0 : give the general form of solutions.
			1 : try easy simplifications
			2 : try more complicated simplification
		
		- ``verb`` - int (default: ``False``) - level of verbosity

	EXAMPLES:

		sage: from eigenmorphic import *
		
		# Fibonnacci
		sage: s = WordMorphism('a->ab,b->a')
		sage: morphic_eigenvalues(s)
		Z*{1, b}
		where b is root of x^2 - x - 1

		# weakly mixing example
		sage: s = WordMorphism('a->aac,b->abcabcc,c->bcc')
		sage: morphic_eigenvalues(s)
		Integer Ring

		# subshift of the regular paperfolding sequence
		sage: t = WordMorphism('a->00,b->01,c->10,d->11')
		sage: s = WordMorphism('a->ca,b->cb,c->da,d->db')
		sage: t(s.fixed_points()[0])
		word: 1101100111001001110110001100100111011001...
		sage: morphic_eigenvalues(s,t)
		1/8Z[1/2]

		# two point extension of Tribonnacci
		sage: s = WordMorphism("A->aB,B->aC,C->a,a->Ab,b->Ac,c->A")
		sage: morphic_eigenvalues(s)
		Z*{1/2*b^2 + 1/2, b, b^2}
		where b is root of x^3 - x^2 - x - 1
		
		# Tribonnacci composed with an erasing morphism
		sage: s = WordMorphism('a->ab,b->ac,c->a')
		sage: t = WordMorphism('a->,b->0,c->1')
		sage: morphic_eigenvalues(s,t)
		Z*{1/2*b^2 + 1/2, b, b^2}
		where b is root of x^3 - x^2 - x - 1

		# substitution coming from an IET
		sage: per = [9, 8, 7, 6, 5, 4, 3, 2, 1] # permutation
		sage: loop = "11010101101100011110000011111010000000110"
		sage: s = rauzy_loop_substitution(per, loop)
		sage: morphic_eigenvalues(s)
		Integer Ring

		# set of eigenvalues in general form
		sage: s = WordMorphism('a->aabc,b->bd,c->dc,d->cab')
		sage: eig = morphic_eigenvalues(s, verb=1); eig
		No simplification of the general form found
		(intersection of Q.{(1, 0, 2, 1), (0, 1, -1, 0)} and the union over n in N of Z^4 mi^n) times (-b + 3, -b + 3, -b + 3, 3*b - 8)
		where b is root of x^2 - 2*x - 2 and mi is the matrix
		[   1 -1/2 -1/2  1/2]
		[   0  1/2 -1/2  1/2]
		[   0 -1/2  1/2  1/2]
		[  -1	1	1   -1]
		sage: eig.approx(100) # compute a subset of the set of eigenvalues
		[1/2]

		# periodic shift
		sage: s = WordMorphism('a->cab,b->c,c->ab')
		sage: morphic_eigenvalues(s, verb=1)
		Periodic subshift with period 3
		1/3Z
		sage: latex(morphic_eigenvalues(s))
		\frac{1}{3}\mathbb{Z}

		#
		sage: s = WordMorphism('a->d,b->c,c->abd,d->bcbc')
		sage: morphic_eigenvalues(s)
		Z[1/b]*{4/5*b^2 + 3/5*b + 1/5, b, b^2}
		where b is root of x^3 - x^2 - 2*x - 2
	"""
	if not s.is_primitive():
		raise ValueError("The substitution s is not primitive !")
	if t is not None and check_periodic:
		from eigenmorphic.recognizability import is_periodic_morphic
		p = is_periodic_morphic(t, s, verb=verb-1)
		if p is not None:
			if verb > 0:
				print("Periodic shift with period %s" % p)
			from sage.rings.rational_field import QQ
			return ModuleEigenvalues([1/QQ(len(p))], 1)
		else:
			if verb > 1:
				print("Aperiodicity checked.")
	if t is not None and check_recognizable:
		from eigenmorphic.recognizability import is_recognizable
		if not is_recognizable(t, s, verb=verb-1):
			raise ValueError("Sorry, I was not able to show that t is recognizable in X_s.\
							 If you don't want to check recognizability, set check_recognizable to False.")
		if verb > 1:
			print("The substitution t is recognizable in the shift of s.")
	if t is None:
		from sage.matrix.special import identity_matrix
		return subshift_eigenvalues(s, m0=identity_matrix(len(s.codomain().alphabet())), check_primitive=False, check_periodic=check_periodic, simplify=simplify, verb=verb)
	return subshift_eigenvalues(s, m0=t.incidence_matrix(), check_primitive=False, check_periodic=False, simplify=simplify, verb=verb)
		

def subshift_eigenvalues(s, m0=None, check_primitive=True, check_periodic=True, simplify=2, verb=False):
	"""
	Give the set of eigenvalues of the subshift of a substitution (or the subshift generated by the image by another substitution if m0 is not None).
	
	INPUT:
	
		- ``s`` - WordMorphism -- the substitution generating the subshift
	
		- ``m0`` - matrix (default: ``None``) - if not None, compute eigenvalues of the subshift generated by the image by tau of the subshift of s, where tau is a substitution of matrix m0 which is assumed recognizable on the subshift of s.
		
		- ``check_periodicity`` - Boolean (default: ``True``) - check if the subshift of the substitution s is periodic
		
		- ``simplify`` - int (default: ``2``) - Level of simplification.
			0 : give the general form of solutions.
			1 : try easy simplifications
			2 : try more complicated simplification
		
		- ``verb`` - bool or int (default: ``False``) - level of verbosity

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import subshift_eigenvalues
		sage: s = WordMorphism('a->ab,b->a')
		sage: subshift_eigenvalues(s)
		Z*{1, b}
		where b is root of x^2 - x - 1

	"""
	from eigenmorphic.coboundary import coboundary_basis
	if check_primitive:
		if not s.is_primitive():
			raise ValueError("The substitution s is not primitive !")
	if check_periodic:
		from eigenmorphic.recognizability import is_periodic
		p = is_periodic(s, getp=True, verb=verb-2)
		if p is not None:
			if verb > 0:
				print("Periodic subshift with period %s" % p)
			return ModuleEigenvalues([1/p], 1)
	else:
		if verb > 2:
			print("periodicity not checked")
	C = list(coboundary_basis(s, verb=verb-1))
	if verb >= 2:
		print("basis of coboundary space :")
		print(C)
	m = s.incidence_matrix()
	if m0 is None:
		from sage.matrix.special import identity_matrix
		m0 = identity_matrix(m.nrows())
	W = eigenvalues_rational_basis(m, C, m0, verb=verb-1)
	v,vp = choose_eigenvector(m, C, m0, getvp=True, verb=verb-2)
	if verb >= 3:
		print("v = %s, vp =%s" % (v, vp))
	K = v[0].parent()
	b = K.gen()
	if verb >= 3:
		print("b=%s (minpoly %s)" % (b, b.minpoly()))
	
	B = simpler_Zmodule(W*v)
	
	if verb >= 2:
		print("B=%s" % B)
		print("W=")
		print(W)
	
	H = vector([1 for _ in range(m0.nrows())])*m0

	if simplify > 0:
		if verb >= 2:
			print("Try to simplify...")
		if abs(m.det()) == 1 or vp == 1 or vp == -1:
			if verb >= 1:
				if abs(m.det()) == 1:
					print("pseudo-unimodular")
				else:
					print("eigenvalue %s" % vp)
			if ((vp == 1 or vp == -1) and v.denominator() == 1) or (len(B) == 1 and (B[0] == 1 or B[0] == -1)):
				return ZZ
			else:
				return ModuleEigenvalues(B, 1)
		elif W.nrows() == W.ncols(): # W is invertible
			if verb >= 1:
				print("W invertible")
			return ModuleEigenvalues(simpler_Zmodule(v), b) #, allK = True) # Z[1/b]*v2
		elif matrix([H, H*m]).rank() == 1: # constant length-like case 
			if verb >= 1:
				print("Constant length-like case")
			if verb >= 2:
				print(H)
				print(H*m)
			return ModuleEigenvalues(B, (H*m)[0]/H[0])
		else:
			if simplify > 1:
				if verb > 2:
					print("Try to find a null power modulo det(m)...")
				# check that m^k is null modulo det(m) for k large enough
				from sage.rings.finite_rings.integer_mod_ring import Integers
				mm = matrix(m, base_ring=Integers(m.det()))
				seen = set()
				mm.set_immutable()
				while mm not in seen:
					seen.add(mm)
					mm = mm*mm
					mm.set_immutable()
				if mm == 0:
					if verb >= 1:
						print("A power of the matrix is null modulo its determinant.")
					return ModuleEigenvalues(B, abs(m.det()))
		if verb >= 1:
			print("No simplification of the general form found")
	return GeneralEigenvalues(m, W, v)

def find_common_number_field (l, name='b'):
	"""
	Find a common NumberField to elements of l.

	INPUT:

		- ``l`` - list of numbers

		- ``name`` - string (default: ``'b'``) -- name of the generator of the result NumberField

	OUTPUT:
		A NumberField

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import find_common_number_field
		sage: find_common_number_field([sqrt(2), sqrt(3)])
		Number Field in b with defining polynomial x^4 - 10*x^2 + 1 with b = 3.146264369941973?
	"""
	from sage.rings.number_field.number_field import NumberField
	from sage.rings.qqbar import QQbar
	from sage.misc.misc_c import prod
	pi = prod([QQbar(t).minpoly() for t in l])
	K = pi.splitting_field(name)
	pi = K.gen().minpoly()
	b = max(pi.roots(ring=QQbar, multiplicities=False))
	return NumberField(pi, 'b', embedding=b)

def eigenvalues_rational_basis (m, c, m0=None, verb=False):
	"""
	Return a matrix W such that eigenvalues of the subshift are
	{ x W v | x W m^n has integer coefficients for n large enough },
	where v is a generalized eigenvector orthogonal to coboundaries

	INPUT:
		- m - matrix -- matrix of the iterated substitution

		- c - matrix -- maximal coboundary of the iterated substitution

		- m0 - matrix (default: ``None``) -- matrix of the first substitution

		- verb - int (default: ``False``) -- if >0, print informations.

	OUTPUT:
		A matrix

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import eigenvalues_rational_basis
		sage: from eigenmorphic.coboundary import coboundary_basis
		sage: s = WordMorphism('a->ab,b->a')
		sage: m = s.incidence_matrix()
		sage: c = coboundary_basis(s)
		sage: eigenvalues_rational_basis(m, c)
		[1 0]
		[0 1]


	"""
	from sage.rings.qqbar import QQbar
	if m0 is None:
		from sage.matrix.special import identity_matrix
		m0 = identity_matrix(m.nrows())
	C = matrix([1 for _ in range(m0.nrows())])*m0
	C = matrix(list(C)+list(c))
	if verb > 0:
		print("C=")
		print(C)
	m = matrix(m, base_ring=QQbar) ##################################
	V = matrix(generalized_eigenvectors(m)[0]).transpose()
	if verb > 0:
		print("V=")
		print(V)
		print("C*V=")
		print(C*V)
	P0 = echelon_form(C*V, only_zeros=True)
	if verb > 0:
		print("P0 =")
		print(P0)
		print("V*P0 =")
		print(V*P0)
	L = [[] for _ in range(V.nrows())]
	for l in (V*P0).columns():
		K = find_common_number_field(l)
		if verb > 2:
			print("field %s" % K)
		for ll,t in zip(L,l):
			ll += K(t).list()
	mvp = matrix(L)
	if verb > 0:
		print("matrix whose left-kernel is the set of w:")
		print(mvp)
	mvp2 = matrix_to_ZZ(mvp)
	if verb > 0:
		print("matrix in Z:")
		print(mvp2)
	W = matrix(mvp2.kernel().basis())
	if verb > 0:
		print("Basis of the Z-module of w:")
		print(W)
	return W


def generalized_eigenvectors (m, c=None, lvp=None, verb=False):
	"""
	Compute a basis of generalized eigenspaces for eigenvalues of modulus >= 1
	If c is not None, keep only vectors orthogonal to c.

	INPUT:
		- m - matrix -- matrix of the iterated substitution

		- c - matrix (default: ``None``) -- basis of the coboundary space

		- lvp - matrix (default: ``None``) -- set of eigenvalues of m

		- verb - int (default: ``False``) -- if >0, print informations.

	OUTPUT:
		A matrix

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import generalized_eigenvectors
		sage: s = WordMorphism('a->ab,b->a')
		sage: m = s.incidence_matrix()
		sage: generalized_eigenvectors(m)
		([(1, 0.618033988749895?)], [1.618033988749895?])

	"""
	from sage.matrix.special import identity_matrix
	if lvp is None:
		lvp = set(m.eigenvalues())
	if c is None:
		c = [[0 for _ in range(m.nrows())]]
		if verb > 1:
			print("c = {}".format(c))
	I = identity_matrix(m.nrows())
	r = []
	rvp = []
	for vp in lvp:
		if abs(vp) >= 1:
			k = m.eigenvalue_multiplicity(vp)
			if verb > 0:
				print("vp = {}, multiplicity = {}".format(vp, k))
			M = (m-vp*I)**k
			KM = M.right_kernel()
			c = matrix(c, base_ring=M.base_ring())
			Kc = c.right_kernel()
			if verb > 2:
				print("K1 = {}".format(KM))
				print("K2 = {}".format(Kc))
			lv = KM.intersection(Kc).basis()
			r += lv
			for _ in lv:
				rvp.append(vp)
	return r, rvp

def echelon_form (m, only_zeros=False, verb=False):
	"""
	Compute the transformation matrix P such that m*P is in column echelon form.
	Does it by the Gauss algorithm.

	INPUT:

		- ``m`` - matrix

		- ``only_zeros`` - bool (default: ``False``) -- if True,
		return only the part of P corresponding to zero columns.

	OUTPUT:
		A matrix

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import echelon_form
		sage: m = matrix([[1,1],[1,1]])
		sage: echelon_form(m)
		[ 1 -1]
		[ 0  1]

		sage: m = matrix([[1,1],[1,1]])
		sage: echelon_form(m, only_zeros=True)
		[-1]
		[ 1]

	"""
	from sage.matrix.special import identity_matrix
	from sage.rings.qqbar import QQbar
	from copy import copy
	
	def swap (m, i, j):
		"""
		Swap columns i and j in m
		"""
		for k in range(m.nrows()):
			t = m[k,i]
			m[k,i] = m[k,j]
			m[k,j] = t

	def transv (m, i, a, j):
		"""
		Do the transvection C_i <-- C_i + a C_j
		"""
		for k in range(m.nrows()):
			m[k,i] += m[k,j]*a

	m = copy(m)
	d = m.ncols()
	P = identity_matrix(d)
	P = matrix(P, base_ring=QQbar)
	cr = 0 # current row
	cc = 0 # current column of pivot
	while True:
		if verb > 0:
			print("cr = %s, cc = %s" % (cr, cc))
			print(m)
		if cr == m.nrows() or cc == m.ncols():
			break
		if m[cr,cc] == 0:
			# find a non-zero coeff in the line
			for i in range(cr+1, d):
				if m[cr,i] != 0:
					if verb > 0:
						print("swap %s and %s" % (i,cc))
					# echange cols i and cc
					swap(m, i, cc)
					swap(P, i, cc)
					break
			else:
				cr += 1
				continue
		# put zeroes after the pivot
		p = m[cr,cc] # pivot
		if verb > 0:
			print("pivot %s" % p)
		for k in range(cc+1,d):
			a = -m[cr,k]/p
			transv(m, k, a, cc)
			transv(P, k, a, cc)
		cc += 1
		cr += 1
	if only_zeros:
		return P.transpose()[cc:d].transpose()
	return P


def matrix_to_ZZ (m, verb=False):
	"""
	Return the smallest integer matrix colinear to m.

	INPUT:

		- m - matrix

		- verb - bool (default: ``False``) -- if >0, print informations.

	OUTPUT:
		A matrix.

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import matrix_to_ZZ
		sage: matrix_to_ZZ(matrix([[1/2, 1/3], [1/3, 1/4]]))
		[6 4]
		[4 3]


	"""
	from sage.arith.functions import lcm
	den = 1
	# compute denominator
	for v in m:
		for t in v:
			den = lcm(den, t.denom())
	if verb > 0:
		print("den = {}".format(den))
	# convert to a matrix in ZZ
	return matrix(m*den, base_ring=ZZ)

def choose_eigenvector (m, C, m0=None, getvp=False, verb=False):
	"""
	Return a generalized eigenvector v of m normalized
	such that (1...1)*m0*v = 1 and Cv = 0,
	for an eigenvalue of modulus >= 1.
	Choose one associated to an eigenvalue
	with smallest discriminant and smallest degree.

	INPUT:

		- m - matrix

		- C - matrix of a basis of coboundary spaces

		- m0 - matrix (default: ``None``)

		- getvp - bool (default: ``False``) -- if True, return also the associated eigenvalue

		- verb - bool (default: ``False``) -- if >0, print informations

	OUTPUT:
		A vector, or a couple (vector, number) if getvp is True

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import choose_eigenvector
		sage: m = matrix([[1,1],[1,1]])
		sage: choose_eigenvector(m, matrix(0,2))
		(1/2, 1/2)

	"""
	from sage.rings.number_field.number_field import NumberField
	from sage.arith.misc import prime_divisors
	if m0 is None:
		from sage.matrix.special import identity_matrix
		m0 = identity_matrix(m.nrows())
	C = matrix(C, ncols=m.ncols())
	# compute the list of eigenvectors
	lv = []
	lvp = []
	for vp,vv,_ in m.right_eigenvectors():
		if abs(vp) >= 1:
			for v in vv:
				if C*v == 0 and sum(m0*v) != 0:
					lv.append(v)
					lvp.append(vp)
	if verb > 0:
		print("lvp = %s" % lvp)
	# compute number of prime numbers for each eigenvalue
	lnp = [len(prime_divisors(vp.minpoly()(0))) for vp in lvp]
	mp = min(lnp)
	if verb > 0:
		print("mp = %s" % mp)
	# keep only vectors with minimal number of prime divisors
	lv2 = []
	lvp2 = []
	for i in range(len(lnp)):
		if lnp[i] == mp:
			lv2.append(lv[i])
			lvp2.append(lvp[i])
	# compute minimal degree
	ld = [vp.minpoly().degree() for vp in lvp2]
	dm = min(ld)
	if verb > 0:
		print("dm = %s" % dm)
	# keep an element with minimal degree
	for v, vp, d in zip(lv2, lvp2, ld):
		if d == dm:
			v = v/sum(m0*v) # renormalize
			K = NumberField(vp.minpoly(), 'b', embedding=vp)
			v = vector([K(t) for t in v])
			if getvp:
				return v, vp
			return v

def simpler_Zmodule (lvp, verb=False):
	"""
	Simplify the basis of the Z-module

	INPUT:

		- lpv - list of NumberField elements

		- verb - bool (default: ``False``) -- if >0, print informations.

	OUTPUT:
		A list of NumberField elements

	EXAMPLES:

		sage: from eigenmorphic.eigenvalues import simpler_Zmodule
		sage: K.<b> = NumberField(x^2-x-1)
		sage: simpler_Zmodule((b^3, b^4-1))
		[1, b]

	"""
	from sage.arith.functions import lcm
	K = lvp[0].parent()
	# convert to a matrix
	mvp = matrix([list(t) for t in lvp])
	if verb > 0:
		print("Corresponding matrix: {}".format(mvp))
	den = 1
	# compute denominator
	for v in mvp:
		for t in v:
			den = lcm(den, t.denom())
	if verb > 0:
		print("den = {}".format(den))
	# convert to a matrix in ZZ
	mvp2 = matrix(mvp*den, base_ring=ZZ)
	if verb > 1:
		print("mvp2 =")
		print(mvp2)
	# compute a basis of the lattice
	mvp3 = mvp2.row_space().basis()
	if verb > 0:
		print("simpler matrix: {}".format(mvp3))
	if verb > 1:
		print("K = {}".format(K))
	# return the basis in the number field
	if K.degree() == 1:
		return [K(t[0])/den for t in mvp3 if K(t[0]) != 0]
	return [K(t)/den for t in mvp3 if K(t) != 0]

def getB(s, t=None, verb=0):
	"""
	Compute a polynomial whose roots of modulus >=1 are the set B defined in Thm 6.3 in "Coboundaries and eigenvalues of morphic subshifts" by P. Mercat

	INPUT:
		- ``s`` - WordMorphism -- the substitution
		- ``t`` - WordMorphism (default: ``None``) -- the pre-period
		- ``verb`` - int (default: 0) -- if >0, print informations

	OUTPUT:
		A polynomial in ZZ, whose roots of modulus >=1 is B.

	EXAMPLES::
		sage: from eigenmorphic.eigenvalues import getB
		sage: s = WordMorphism('a->ab,b->cb,c->ad,d->cd')
		sage: t = WordMorphism('a->11,b->01,c->10,d->00')
		sage: getB(s, t)
		x - 2
		sage: s = WordMorphism('1->16,2->122,3->12,4->3,5->124,6->15')
		sage: getB(s)
		x^6 - 3*x^5 + x^4 + x^3 + x^2 - x + 1
	"""
	m = s.incidence_matrix()
	if t is None:
		mt = identity_matrix(m.nrows()) # matrix of pre-period
	else:
		mt = t.incidence_matrix()
	fl = vector((1 for _ in range(mt.nrows())))*mt
	if verb > 0:
		print("linear form", fl)
	xi = m.minpoly()
	L = xi.parent()
	f0 = L(1)
	res = L(1)
	for f,k in xi.factor():
		if f(0) == 0:
			if verb > 0:
				print("skip", f**k)
			continue
		if verb > 0:
			print(f)
		if f.is_cyclotomic():
			if verb > 1:
				print(" -> cyclotomic")
			f0 *= (f**k)
		else:
			mf = matrix((f**k)(m).right_kernel().basis()).transpose()
			if verb > 0:
				print(mf)
				print(fl*mf)
			if not (fl*mf).is_zero():
				res *= f
	R = coboundary_basis(s).right_kernel()
	if verb > 0:
		print("R =", R)
	G0 = f0(m).right_kernel()
	if verb > 0:
		print("G0 =", G0)
	mi = matrix((R.intersection(G0)).basis(), ncols=m.ncols()).transpose()
	if verb > 0:
		print("mi =")
		print(mi)
		print(fl*mi)
	if not (fl*mi).is_zero():
		res *= f0
	return res

def graph_of_algebraic_numbers(p, verb=0):
	"""
	Compute the graph of algebraic numbers roots of p.
	
	INPUT:
		- ``p`` - Polynomial
		- ``verb`` - int (default: 0) -- if >0, print informations

	OUTPUT:
		A graph.

	EXAMPLES::
		sage: from eigenmorphic.eigenvalues import getB, graph_of_algebraic_numbers
		sage: s = WordMorphism('a->ab,b->cb,c->ad,d->cd')
		sage: t = WordMorphism('a->11,b->01,c->10,d->00')
		sage: graph_of_algebraic_numbers(getB(s, t))
		Looped digraph on 1 vertex
		sage: s = WordMorphism('1->16,2->122,3->12,4->3,5->124,6->15')
		sage: graph_of_algebraic_numbers(getB(s))
		Looped digraph on 6 vertices
	"""
	# compute the Galois group
	r = max(p.roots(ring=QQbar))[0]
	K = p.splitting_field('a')
	K = NumberField(K.defining_polynomial(), 'a', embedding=r)
	G = K.galois_group()
	if verb > 0:
		print(G)
	# vertices of the graph
	V = {K(r) for r,_ in p.roots(ring=QQbar)}
	if verb > 0:
		print("vertices:", V)
	B = {b for b in V if abs(b) >= 1}
	edges = {(b1, b2) for b1 in B for b2 in B}
	# stabilize the set of edges by the Galois group
	edges2 = set()
	for g in G:
		for (b1, b2) in edges:
			edges2.add((g(b1), g(b2)))
	edges = edges2
	return DiGraph(list(edges), loops=1)

def dimension_eigenvalues(s, t=None, verb=0):
	"""
	Return the dimension of the Q-vector space generated by additive eigenvalues of the subshift of s, with pre-period t.
	
	INPUT:
		- ``s`` - WordMorphism -- the substitution
		- ``t`` - WordMorphism (default: ``None``) -- the pre-period
		- ``verb`` - int (default: 0) -- if >0, print informations

	OUTPUT:
		A polynomial in ZZ, whose roots of modulus >=1 is B.

	EXAMPLES::
		sage: from eigenmorphic import *
		sage: s = WordMorphism('a->ab,b->cb,c->ad,d->cd')
		sage: t = WordMorphism('a->11,b->01,c->10,d->00')
		sage: dimension_eigenvalues(s, t)
		1
		sage: s = WordMorphism('1->16,2->122,3->12,4->3,5->124,6->15')
		sage: dimension_eigenvalues(s)
		3
	"""
	p = getB(s, t, verb-1)
	if verb > 0:
		print("polynomial for B :", p)
	g = graph_of_algebraic_numbers(p, verb-1)
	if verb > 0:
		print("graph :", g)
	return g.connected_components_number()
	
