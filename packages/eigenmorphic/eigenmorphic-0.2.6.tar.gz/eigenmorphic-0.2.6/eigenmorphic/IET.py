from sage.modules.free_module_element import vector
from copy import copy

def per_to_e(per, start=1):
	"""
	Convert a permutation given as a list of images or other entries,
	and return a couple (list of integers before, list of integers after).
	
	start : smallest integer (0 or 1)
	"""
	if isinstance(per, str):
		per = [int(c) for c in per] # convert it to numbers
	try:
		e = [list(per[0]), list(per[1])]
	except:
		m = min(per)
		e = [list(range(start,len(per)+start)), [i+start-m for i in per]]
	return e

def e_to_per(e):
	"""
	Convert the permutation to a list of images,
	permurt l accordingly.
	"""
	from sage.groups.perm_gps.permgroup_named import SymmetricGroup
	G = SymmetricGroup(len(e[0]))
	p1 = G(e[0])
	p2 = G(e[1])
	p = p2*p1**(-1)
	return tuple(p(i+1) for i in range(len(e[0]))) #, vector([x for _,_,x in lp])

def induce(e, i, flipped, gets2=0, verb=0):
	"""
	Compute one step of induction on place, and return the associated substitution.
	e : couple of lists, before and after exchange
	i : top or bottom induction (i=0: bottom losing letter, i=1: top losing letter)
	"""
	from sage.combinat.words.morphism import WordMorphism
	if i == 0:
		i0 = 0
		i1 = 1 # losing letter
	else:
		i0 = 1
		i1 = 0 # losing letter
	d = dict()
	if gets2:
		d2 = dict()
	for i in e[0]:
		d[i] = [i]
		if gets2:
			d2[i] = [i]
	d[e[i1][-1]] = [e[1][-1], e[0][-1]] # 1 0
	if gets2:
		d2[e[i0][-1]] = [e[i0][-1], e[i1][-1]]
		if verb > 0:
			print("%s -> %s %s" % (e[i0][-1], e[i0][-1], e[i1][-1]))
	if flipped[e[i0][-1]]:
		from operator import xor
		e[i1].insert(e[i1].index(e[i0][-1]), e[i1][-1])
		flipped[e[i1][-1]] = not flipped[e[i1][-1]]
	else:
		e[i1].insert(e[i1].index(e[i0][-1])+1, e[i1][-1])
	e[i1].pop()
	if gets2:
		return WordMorphism(d), WordMorphism(d2)
	else:
		return WordMorphism(d)

def induce_list(per, li, l=None, flips=None):
	"""
	Compute the sequence of inductions from e.
	
	NE MARCHE PAS DU TOUT POUR UNE RAISON INEXPLICABLE !!!!!
	
	per : the permutation
	li : list of inductions (0 or 1)
	l : list of lengths (default: None)
	flips : flips
	"""
	if l:
		v = vector(l)
	if isinstance(li, str):
		li = [int(c) for c in li] # convert it to numbers
	if flips is None:
		flips = {i:False for i in range(1,len(per)+1)}
	e = per_to_e(per)
	for i in li:
		s = induce(e, i, flips)
		if l:
			m = s.incidence_matrix()
			v = m.inverse()*v
			v /= sum(v)
	if l:
		return e, v
	else:
		return e

def which_int (x, v):
	"""
	Return the index of the interval in which is x, where v gives lengths.
	"""
	from sage.functions.generalized import sign
	s = 0
	for i,t in enumerate(v):
		s += t
		if sign(s-x) == 1:
			return i

def translation (i, p, v):
	"""
	Compute the translation of ith interval.
	"""
	s = 0
	for j in p:
		if j == i+1:
			break
		s += v[j-1]
	for j in range(i):
		s -= v[j]
	return s

def IET (x, p, v):
	"""
	Compute the image of x by the IET given by permutation p and lengths v
	"""
	i = which_int(x,v)
	s = 0
	for j in p:
		if j == i+1:
			break
		s += v[j-1]
	for j in range(i):
		s -= v[j]
	return x+s

def orbit (x, per, v, N=20):
	"""
	Compute N steps of the orbit of x.

	INPUT:

		- ``x`` - a number

		- ``per`` - permutation, given as a string or list of int

		- ``v`` - vector of lengths

		- ``N`` - length of the orbit to compute

	EXAMPLES::

		sage: from eigenmorphic import *
		sage: orbit(random(), "321", [.23, .34, .43])		# random
		word: 31313231322313223132

	"""
	from sage.combinat.words.word import Word
	if isinstance(per, str):
		per = [int(c) for c in per]
	lt = [translation(i, per, v) for i in range(len(per))]
	w = []
	for _ in range(N):
		i = which_int(x,v)
		w.append(i+1)
		x = x + lt[i]
	return Word(w)

def rauzy_path_substitution(per, path, flips=None, get_per=True, verb=False):
	from sage.combinat.words.morphism import WordMorphism
	if isinstance(per, str):
		per = [int(c) for c in per] # convert it to numbers
	e = per_to_e(per)
	if verb > 0:
		print("e = %s" % e)
	if isinstance(path, str):
		path = [int(c) for c in path] # convert it to numbers
	if verb > 0:
		print("path = %s" % path)
	if flips is None:
		f = {i:False for i in range(1,len(e[0])+1)}
	else:
		f = copy(flips)
	if verb > 0:
		print("flips = %s" % f)
	d = dict()
	for i in e[0]:
		d[i] = [i]
	s = WordMorphism(d)
	for i in path:
		if verb > 0:
			print(e)
			print(f)
		s0 = induce(e, i, f)
		if verb > 0:
			print(s0)
		s = s*s0
	if verb > 0:
		print(e)
		print(f)
		print(s)
		print("per = %s" % per)
	if get_per:
		return s, e #[e[0].index(t)+1 for t in e[1]]
	return s

def rauzy_loop_substitution(per, loop, flips=None, max_len=1000, stop=-1, get_preperiod=False, get_cmp=False, getls=0, gets2=0, verb=False):
	"""
	Compute the susbtitution of a loop in the Rauzy graph from a given permutation per.

	INPUT:

		- ``per`` - list -- a permutation
			The i-th element of the list is the image of (i+1) by the permutation.

		- ``loop`` - list or string or vector -- list with values in {0,1} indicating which rauzy induction
			where 0 indicate that the losing letter is at bottom and
				  1 indicate that the losing letter is at top
			or vector of lengths (with same length as per).

		- ``flips`` - dict (default: ``None``) -- dictionnary indicating for each letter whether it is flipped (value True) or not (value False).

		- ``max_len`` - int (default: ``1000``) - maximum length of the Rauzy loop if a vector of lengths is given

		- ``get_preperiod`` - bool (default: ``False``) - if ``True``, return a couple of substitutions corresponding to (pre-period, period)
		
		- ``get_cmp`` - bool (default: ``False``) - if ``True``, return the list of comparaisons

		- ``verb`` - int (default: ``False``) - if >0, print informations.

	OUTPUT:
		A WordMorphism

	EXAMPLES:

		sage: from eigenmorphic import *
		sage: per = [9, 8, 7, 6, 5, 4, 3, 2, 1] # permutation
		sage: loop = "11010101101100011110000011111010000000110"
		sage: rauzy_loop_substitution(per, loop)
		WordMorphism: 1->17262719, 2->172627262719, 3->172635362719, 4->1726354445362719, 5->172635445362719, 6->1726362719, 7->172719, 8->18181819, 9->181819

		sage: a = AA(2*cos(pi/7))
		sage: l = [1, 2*a-3, 2-a, a^2-a, 2*a^2-3*a-1, -3*a^2+5*a+1]
		sage: rauzy_loop_substitution([4,3,2,6,5,1], l)
		WordMorphism: 1->14164, 2->142324, 3->1423324, 4->1424, 5->154154164, 6->154164

		# example from N. Bédaride
		sage: a = AA(2*cos(pi/7))
		sage: A = (-10*a^2 + 6*a + 25)/13
		sage: B = (24*a^2 - 17*a - 47)/13
		sage: C = (-19*a^2 + 14*a + 41)/13
		sage: D = (6*a^2 -a -15)/13
		sage: E = (15*a^2 - 9*a -31)/13
		sage: F = (-16*a^2 + 7*a + 40)/13
		sage: l = [A,B,C,D,E,F]
		sage: from eigenmorphic.balanced_pair_algo import convert_substitution
		sage: per = [3, 2, 5, 1, 6, 4]
		sage: pre, s = rauzy_loop_substitution(per, l, get_preperiod=True, verb=0)
		sage: pre,_ = convert_substitution(pre)
		sage: s,_ = convert_substitution(s)
		sage: pre, s
		(WordMorphism: 0->02, 1->1, 2->2, 3->0335342, 4->0342, 5->033535342,
		 WordMorphism: 0->0402, 1->012, 2->01202, 3->04353402, 4->043402, 5->043553402)

	"""
	from copy import copy
	from sage.combinat.words.morphism import WordMorphism
	if isinstance(per, str):
		per = [int(c) for c in per] # convert it to numbers
	e = per_to_e(per)
	e0 = (tuple(e[0]), tuple(e[1]))
	if flips is None:
		f = {i:False for i in range(1,len(e[0])+1)}
	else:
		f = copy(flips)
	f0 = copy(f)
	if verb > 0:
		print("flips = %s" % f)
	d = dict()
	for i in e[0]:
		d[i] = [i]
	s = WordMorphism(d)
	if gets2:
		s2 = WordMorphism(d)
	if isinstance(loop, str):
		loop = [int(c) for c in loop] # convert it to numbers
	if verb > 1:
		print("per = %s, loop = %s" % (per, loop))
	ls = []
	if len(loop) == len(e[0]) and len([i for i in loop if i not in [0,1]]) != 0:
		if verb > 0:
			print("loop is a vector")
		v = vector(loop)
		v /= sum(v)
		v0 = vector(v)
		seen = dict()
		if gets2:
			ls2 = []
		lcmp = []
		for i in range(max_len):
			cmp = int(v[e[0][-1]-1] < v[e[1][-1]-1])
			if verb > 1:
				print(cmp)
			lcmp.append(cmp)
			if gets2:
				s0, s20 = induce(e, cmp, flipped=f, gets2=1)
				s2 = s20*s2
				ls2.append(s20)
			else:
				s0 = induce(e, cmp, flipped=f)
			if verb > 0:
				print(s0)
			if verb > 1:
				print(e)
			s = s*s0
			m = s0.incidence_matrix()
			v = m.inverse()*v
			if verb > 1:
				print(v)
			v /= sum(v)
			if v == v0:
				ls.append(s0)
				break
			if tuple(v) in seen:
				if get_preperiod:
					from sage.misc.misc_c import prod
					i = seen[tuple(v)]
					if get_cmp:
						return (lcmp[:i], prod(ls[:i])), (lcmp[i:], prod(ls[i:]+[s0]))
					else:
						return prod(ls[:i]), prod(ls[i:]+[s0])
				else:
					raise ValueError("It is pre-periodic with a non-trivial pre-period (you can compute it with option get_preperiod=True).")
			seen[tuple(v)] = i+1
			ls.append(s0)
			if verb > 1:
				print(v)
				#print([t.n() for t in v])
			stop -= 1
			if not stop:
				return e, v
		else:
			raise ValueError("The given lengths vector does not give a loop, or the loop is longer than max_len=%s. Try with bigger max_len." % max_len)
	else:
		if verb > 0:
			print("loop is a list of inductions")
		for i in loop:
			if verb > 0:
				print(e)
				print(f)
			s0 = induce(e, i, f)
			ls.append(s0)
			if verb > 0:
				print(s0)
			s = s*s0
		if verb > 0:
			print(e)
			print(f)
			print(s)
			print("per = %s" % per)
		# check if it is indeed a loop
		for i in range(len(e[0])):
			if e[0][i] != e0[0][i] or e[1][i] != e0[1][i]:
				raise ValueError("This is not a loop in the Rauzy graph !\n%s != %s" % (e, e0))
		if f != f0:
			raise ValueError("This is not a loop in the Rauzy graph (flips are different) !\n%s != %s" % (f, f0))
	if get_preperiod:
		return lcmp
	if getls:
		if gets2:
			return ls, ls2
		return ls
	else:
		if gets2:
			if get_cmp:
				return lcmp,s, s2
			return s, s2
		else:
			if get_cmp:
				return lcmp,s
			return s

##############
# tools to plot a Surface with fixed points of Anosov
##############

def rectangle(l, h, x, y, color = "white"):
	from sage.plot.polygon import polygon2d
	return polygon2d([(x,y), (x+l,y), (x+l,y+h), (x,y+h)], color=color, fill=0)

def plot_rectangles(vl, vh, lp=None, color = "white"):
	from sage.plot.graphics import Graphics
	from sage.plot.point import points
	g = Graphics()
	x = 0
	for i in range(len(vl)):
		if lp:
			g += points([(x2+x,y2) for x2,y2 in lp[i]], color=color)
		g += rectangle(vl[i], vh[i], x, 0, color=color)
		x += vl[i]
	g.axes(0)
	g.SHOW_OPTIONS['transparent'] = 1
	return g

def paths(ls):
	A = ls[0].domain().alphabet()
	lc = [[i] for i in A]
	for s in ls:
		lc2 = []
		for c in lc:
			for j in s(c[-1]):
				lc2.append(c+[j])
		lc = lc2
	return lc

def convert_IET(per, v, verb=0):
	"""
	Convert the data to (permutation (before, after), vector of lengths).
	
	per : permutation
	v : vector of lengths, or loop in the graph of graphs
	"""
	e = per_to_e(per)
	if verb > 0:
		print("e =", e)
	if isinstance(v, str):
		v = [int(c) for c in v] # convert it to numbers
	if len(v) == len(e[0]) and len([i for i in v if i not in [0,1]]) != 0:
		if verb > 0:
			print("v is a vector")
	else:
		s = rauzy_loop_substitution(e, v)
		m = s.incidence_matrix()
		v = max(m.right_eigenvectors())[1][0]
		v /= sum(v)
		if verb > 0:
			print("vector of lengths:", v)
	# convert the up permutation to identity
	v = [v[i-1] for i in e[0]]
	e = [list(range(1, len(v)+1)), [e[0].index(i)+1 for i in e[1]]]
	#
	return e, v

def anosov_fixed_points(per, v, s=None, s2=None, vh=None, verb=0):
	"""
	Compute the list of fixed points of the pseudo-Anosov map.

	INPUT:
		per : permutation
		v : vector of lengths, or loop in the graph of graphs

	OUTPUT:
		A list of list of points (one list per rectangle), in the coordinates of the corresponding rectangle.

	EXAMPLES::
		sage: from eigenmorphic import *
		sage: anosov_fixed_points("321", "010101101")
		[[[0, 0], [0.10334828131703736?, 0.12153156246905968?]],
		 [[0.0866068747318506?, 0.03588593744843280?],
		  [0.3366068747318506?, 0.07177187489686560?],
		  [0.1899551560488880?, 0.1574174999174925?],
		  [0.4399551560488880?, 0.1933034373659253?],
		  [0.04330343736592527?, 0.2430631249381194?],
		  [0.2933034373659253?, 0.2789490623865522?],
		  [0.1466517186829627?, 0.3645946874071790?],
		  [0.3966517186829627?, 0.4004806248556119?],
		  [0, 0.4502403124278059?],
		  [0.2500000000000000?, 0.4861262498762388?]],
		 [[0.2933034373659253?, 0.02201218732467152?],
		  [0.1466517186829627?, 0.10765781234529840?],
		  [0.3966517186829627?, 0.1435437497937312?],
		  [0, 0.1933034373659253?]]]
	"""
	e, v = convert_IET(per, v, verb=verb-1)
	if s is None or s2 is None:
		s,s2 = rauzy_loop_substitution(per, v, gets2=1)
		assert(s.incidence_matrix().transpose() == s2.incidence_matrix())
	vl = v
	if vh is None:
		vh = max(s.incidence_matrix().left_eigenvectors())[1][0]
		vh /= sum(vh)
		if verb > 0:
			print("vector of highs :", vh)
	ls, ls2 = rauzy_loop_substitution(per, v, getls=1, gets2=1)
	from sage.misc.misc_c import prod
	assert(prod(ls) == s)
	assert(prod(reversed(ls2)) == s2)
	lp = paths(list(reversed(ls)))
	lp2 = paths(list((ls2)))
	if verb > 0:
		print("%s paths found." % len(lp))
	assert(len(lp) == len(lp2))
	# Perron eigenvalue
	lamb = max(s.incidence_matrix().eigenvalues())
	if verb > 0:
		print("Perron eig:", lamb)
	# compute first coordinate of each fixed point
	d = dict()
	ri = 0
	for l in lp:
		if l[0] != ri:
			ri = l[0]
			k = 0
		if l[0] == l[-1]:
			d[tuple(l)] = sum(map(lambda i:vh[i-1], s(l[0])[:k]))/(lamb-1)
		k += 1
	if verb > 0:
		print("nbr of fixed pts:", len(d))
	# compute the other coordinate
	ri = 0
	d2 = dict()
	for l in lp2:
		if l[0] != ri:
			ri = l[0]
			k = 0
		if l[0] == l[-1]:
			t = tuple(reversed(l))
			if t not in d:
				raise ValueError("not in d")
			x = sum(map(lambda i:vl[i-1], s2(l[0])[:k]))/(lamb-1)
			d2[t] = [x, d[t]]
		k += 1
	L = [[] for _ in range(len(vl))]
	for l in d:
		L[l[0]-1].append(d2[l])
	return L

def plot_surface_with_fixed_pts(per, v, color = "white", verb=0):
	"""
	Plot the surface and fixed points of the Anosov corresponding to the given IET.

	INPUT:
		per : permutation
		v : vector of lengths, or path in the Rauzy graph
	
	OUTPUT:
		A Graphics object.

	EXAMPLES::
		sage: from eigenmorphic import *
		sage: plot_surface_with_fixed_pts("321", "010101101010")
		Graphics object consisting of 6 graphics primitives
		
		sage: v = [4*b^2 - 2*b - 9, -7*b^2 + 6*b + 12, 5*b^2 - 4*b - 9, -b + 2, -3*b^2 + b + 8, b^2 - 3]
        sage: per = "643215"
        sage: plot_surface_with_fixed_pts(per, v)
	"""
	from sage.plot.graphics import Graphics
	e,v = convert_IET(per, v, verb=verb-1)
	s,s2 = rauzy_loop_substitution(e, v, gets2=1)
	assert(s.incidence_matrix().transpose() == s2.incidence_matrix())
	if verb > 0:
		print(s, s2)
	vl = v
	vh = max(s.incidence_matrix().left_eigenvectors())[1][0]
	vh /= sum(vh)
	if verb > 0:
		print("vector of highs :", vh)
	# compute fixed points
	L = anosov_fixed_points(e, v, s=s, s2=s2, vh=vh, verb=verb)
	# plot
	return plot_rectangles(vl, vh, L, color=color)

def plot_bratteli(ls, colors = ["white", "yellow"], transparent=True, ratio=1):
	"""
	Plot the Bratteli diagram corresponding to the list of substitutions ls.
	
	INPUT:
		ls : list of WordMorphism
		colors : list of colors, corresponding to ordering of edges

	OUTPUT:
		A Graphics objetc.

	EXAMPLES::
		sage: from eigenmorphic import *
		sage: ls = [WordMorphism({0:[0,1],1:[0,2],2:[0]}), WordMorphism({0:[0],1:[1],2:[0,1]})]
		sage: plot_bratteli(ls)
		Graphics object consisting of 9 graphics primitives
		
		sage: ls = rauzy_loop_substitution("321", "010101", getls=1)
		sage: plot_bratteli(ls)
		Graphics object consisting of 24 graphics primitives
	"""
	from sage.plot.graphics import Graphics
	from sage.plot.bezier_path import bezier_path

	def path(i,j,k, color):
		return bezier_path([[(i,k),(i,.5+k),((i+j)/2,k+.5)],[((i+j)/2,k+.5),(j,k+.5),(j,k+1)]], color=color, thickness=1)

	s = ls[0]
	g = Graphics()
	for k,s in enumerate(ls):
		for i in s.domain().alphabet():
			for a,j in enumerate(s(i)):
				g += path(i*2,j*2,-k, color=colors[a])
	g.axes(0)
	g.set_aspect_ratio(ratio)
	g.SHOW_OPTIONS['transparent'] = transparent
	return g

########
# tools to compute the graph of graphs
########

def induction(e0, i):
	"""
	One step of Rauzy induction for the IET combinatorics.

	e0 : couple (list of intervals before, list of intervals after)
	i : which induction (0: top, 1: bottom)
	"""
	e = [list(e0[0]), list(e0[1])]
	if i==0:
		e[0].insert(e[0].index(e[1][-1])+1, e[0][-1])
		e[0].pop()
	else:
		e[1].insert(e[1].index(e[0][-1])+1, e[1][-1])
		e[1].pop()
	return e

def hashable(e):
	"""
	Make e hashable.
	"""
	return (tuple(e[0]), tuple(e[1]))

def e_to_str(e):
	"""
	Convert the permutation e to str.
	The permutation is assumed to be from 0.
	"""
	from sage.groups.perm_gps.permgroup_named import SymmetricGroup
	G = SymmetricGroup(range(len(e[0])))
	p1 = G(list(e[0]))
	p2 = G(list(e[1]))
	p = p2*p1**(-1)
	res = ""
	for i in range(len(e[0])):
		res += str(p(i)+1)
	return res

def graph_of_graphs(e):
	"""
	Compute the graph of graphs from state e.
	
	INPUT:
		e : permutation, given as a list of images, or a couple (before, after)

	OUTPUT:
		A DiGraph.

	EXAMPLES::
		sage: from eigenmorphic import *
		sage: g = graph_of_graphs("321")
		sage: g.plot(edge_labels=1)			# not tested
	"""
	from sage.graphs.digraph import DiGraph
	
	class DiGraph2(DiGraph):
		def plot(self, **options):
			options['edge_labels'] = True
			return DiGraph.plot(self, **options)
	
	e = per_to_e(e, start=0)
	to_see = [e]
	seen = set([hashable(e)])
	L = []
	while len(to_see) > 0:
		e = to_see.pop()
		es = hashable(e)
		for i in range(2):
			e2 = induction(e, i)
			es2 = hashable(e2)
			if es2 not in seen:
				seen.add(es2)
				to_see.append(e2)
			L.append((e_to_str(es), e_to_str(es2), i))
	return DiGraph2(L, loops=1, multiedges=1)

