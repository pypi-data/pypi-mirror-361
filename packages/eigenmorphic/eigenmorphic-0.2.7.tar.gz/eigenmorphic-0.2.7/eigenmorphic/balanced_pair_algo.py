from sage.rings.integer_ring import ZZ
from sage.rings.rational_field import QQ
from sage.combinat.words.word import Word
from .matrix import matrix
from sage.matrix.special import identity_matrix
from sage.modules.free_module_element import vector
from eigenmorphic.eigenvalues import dimension_eigenvalues, morphic_eigenvalues, is_pisot, getB
from eigenmorphic.coboundary import coboundary_basis
from sage.rings.number_field.number_field import NumberField
from sage.modules.free_module import VectorSpace
from sage.arith.functions import lcm
from sage.combinat.words.morphism import WordMorphism
from eigenmorphic.coboundary import return_substitution
#from sage.combinat.words.morphism import WordMorphism

def return_words(s, w=None, verb=0):
    """
    Find return words on w for sustitution s,
    where w is a prefix of a fixed point of s.
    If w is None, take first letter of a fixed point.

    A word u is a return word for w if
    - uw is in the language of s,
    - w is a prefix of u, and there is no other occurence of w in u

    INPUT:
        - ``s`` - WordMorphism - the substitution
        - ``w`` - Word (default: ``None``) - a prefix of a fixed point of s
        - ``verb`` - int (default: 0) - If > 0, print informations

    OUTPUT:
        A set of return words.

    EXAMPLES::
        sage: from eigenmorphic import *
        sage: s = WordMorphism('1->112,2->2321,3->12')
        sage: return_words(s, '1')
        {word: 1, word: 12, word: 12232, word: 1232}
        sage: s = WordMorphism('0->2021,1->21,2->20')
        sage: return_words(s, '202')
        {word: 202021, word: 2021}
    """
    if w is None:
        w = s.fixed_points()[0][:1]
        if verb > 0:
            print("w = " + str(w))
    else:
        w = Word(w, alphabet=s.domain().alphabet())
    w0 = w
    while True:
        if len(w0) > len(w):
            if w0[:len(w)] != w:
                raise ValueError("%s must be the prefix of a fixed point" % w)
            if verb > 1:
                print("Find %s in %s..." % (w, w0))
            #i = w0.find(w, start=1)
            for i in range(len(w), len(w0)-len(w)+1):
                if w0[i:i+len(w)] == w:
                    break
            else:
                w0 = s(w0)
                continue
            break
        w0 = s(w0)
    w0 = w0[:i]
    if verb > 0:
        print("first return word : %s" % w0)
    to_see = set([w0])
    res = set(to_see)
    while len(to_see) > 0:
        to_see2 = set()
        for r in to_see:
            r2 = s(r)
            if verb > 2:
                print("s(%s) = %s" % (r, r2))
            if r2[:len(w)] != w:
                raise ValueError("The word %s must be a prefix of a fixed point of the susbtitution." % w)
            ri = 0
            i = len(w)
            while i <= len(r2)-len(w):
                if r2[i:i+len(w)] == w:
                    r3 = r2[ri:i]
                    if r3 not in res:
                        res.add(r3)
                        to_see2.add(r3)
                    ri = i
                    i += len(w)
                else:
                    i += 1
            r3 = r2[ri:]
            if r3 not in res:
                res.add(r3)
                to_see2.add(r3)
        to_see = to_see2
    return res

def proprify(s, verb=0):
    """
    Return a substitution whose subshift is conjugate to s.
    """
    p = 1
    while len((s**p).fixed_points()) == 0:
        p += 1
    #s = s**p
    if verb > 0:
        print("p =",p)
    rs, rw = return_substitution(s**p, getrw=True)
    lr = list(rw)
    if verb > 0:
        print(rs)
        print(rw)
    def ok(t):
        for i in t.domain().alphabet():
            if len(t(i)) < len(lr[i]):
                return False
        return True
    p = 1
    while not ok(rs**p):
        p += 1
    rs = rs**p
    if verb > 0:
        print("p = ", p)
    B = [(r,p) for r in range(len(rw)) for p in range(len(lr[r]))]
    if verb > 0:
        print(B)
    def psi(w):
        res = []
        for l in w:
            res += [(l,i) for i in range(len(lr[l]))]
        return res
    
    d = dict()
    for (r,p) in B:
        if p < len(lr[r])-1:
            d[(r,p)] = psi(rs(r)[p:p+1])
        else:
            d[(r,p)] = psi(rs(r)[len(lr[r])-1:])
    if verb > 0:
        print(d)
    d2 = {B.index(e):[B.index(f) for f in d[e]] for e in B}
    return WordMorphism(d2)

def is_balanced(u,v, pv=None):
    """
    Test if a couple of words is balanced for projection pv.

    INPUT:
        - ``u`` - Word
        - ``v`` - Word
        - ``pv`` - (default: ``None``) - vector or matrix - projection

    OUPTUT:
        A bool.

    EXAMPLES::
        sage: from eigenmorphic.balanced_pair_algo import is_balanced
        sage: w = Word('1221', alphabet=list('123'))
        sage: is_balanced(w[:2], w[2:], vector((1,1,1)))
        True
        sage: is_balanced(w[:2], w[2:])
        True
    """
    if pv is None:
        pv = identity_matrix(u.parent().alphabet().cardinality())
    return pv*(vector(u.abelian_vector()) - vector(v.abelian_vector())) == 0

def is_prefix(w, s):
    """
    Determine if w is a prefix of a fixed point of s.
    Assume that w[:1] is a prefix of a fixed point of s.
    """
    return w.is_prefix(s.fixed_point(w[:1][0]))

def decompose(u, v, pv=None, pvr=None, verb=0):
    """
    Decompose a balanced pair into irreducible pairs, for a projection pv.
    The substitution is assumed to have alphabet [0,1,...]

    INPUT:
        - ``u`` - Word
        - ``v`` - Word
        - ``pv`` - vector or matrix (default: ``None``) - projection
        - ``pvr`` - vector (default: ``None``) - length vector in RR
        - ``verb`` - int (default: ``0``) - if > 0, print informations

    OUTPUT:
        List of irreducible balanced pairs (list of couples of words)

    EXAMPLES::
        sage: from eigenmorphic.balanced_pair_algo import decompose
        sage: s = WordMorphism({0:[0,1],1:[0,2],2:[0]})
        sage: decompose(s([0,1]), s([1,0]))
        [(word: 0, word: 0), (word: 102, word: 201)]
    """
    if pv is None:
        pv = identity_matrix(u.parent().alphabet().cardinality())
    if pvr is None:
        pvr = vector((1 for _ in range(pv.ncols())))
    r = []
    ri1 = 0
    ri2 = 0
    i1 = 1
    i2 = 1
    l1 = pvr[u[0]]
    l2 = pvr[v[0]]
    v1 = pv[:,u[0]]
    v2 = pv[:,v[0]]
    eps = min(pvr)/2
    if verb > 0:
        print()
        print("decompose %s %s" % (u,v))
    for i in range(len(u)+len(v)-1):
        if verb > 1:
            print("i1=%s, i2=%s ri1=%s, ri2=%s" % (i1,i2, ri1, ri2))
        if l1 - eps < l2 < l1 + eps:
            if (v1-v2).is_zero():
                r.append((u[ri1:i1],v[ri2:i2]))
                if verb > 0:
                    print("r=",r)
                ri1 = i1
                ri2 = i2
                if i == len(u)+len(v)-2:
                    break
        if l1 < l2:
            l1 += pvr[u[i1]]
            v1 += pv[:,u[i1]]
            i1 += 1
        else:
            l2 += pvr[v[i2]]
            v2 += pv[:,v[i2]]
            i2 += 1
    #if i1 != ri1 or ri2 != i2:
    #    raise RuntimeError("Error in decomposition")
    return r

def first_balanced_pairs(s, w, pv, pvr, verb=0):
    """
    First set of balanced pairs in the balanced pair algorithm.
    The substitution is assumed to have alphabet [0,1,...]

    INPUT:
        - ``s`` - WordMorphism - the substitution, assumed to have a fixed point
        - ``w`` - Word - prefix of a fixed point of s
        - ``pv`` - (default: ``None``) - vector or matrix - projection
        - ``pvr`` - (default: ``None``) - length vector with float coordinates
        - ``verb`` - int (default: 0) - If > 0, print informations

    OUTPUT:
        A set of balanced pairs (couples of words).

    EXAMPLES::
        sage: from eigenmorphic.balanced_pair_algo import first_balanced_pairs
        sage: s = WordMorphism({0:[0,0,1],1:[1,2,1,0],2:[0,1]})
        sage: first_balanced_pairs(s, Word([1], alphabet=[0,1,2]), identity_matrix(3), vector((1,1,1)))
        {(word: 1, word: 1),
         (word: 10, word: 01),
         (word: 100, word: 001),
         (word: 1000, word: 0001),
         (word: 12, word: 21)}
    """
    lr = return_words(s, w, verb-1)
    lb = [(u, u[len(w):]+w) for u in lr]
    lb2 = set()
    for u,v in lb:
        for u2,v2 in decompose(u, v, pv, pvr, verb=verb-3):
            if (v2,u2) in lb2:
                v2, u2 = u2, v2 # swap
            lb2.add((u2, v2))
    return lb2

def convert_substitution(s, A=None):
    """
    Convert a substitution with alphabet of indices.

    INPUT:
        - s - WordMorphism - the substitution
        - A - list - the ordered alphabet of the substitution

    OUTPUT:
        A WordMorphism and a list (ordered alphabet)

    EXAMPLES::
        
    """
    if A is None:
        A = list(s.domain().alphabet())
    d = dict()
    for a in A:
        d[A.index(a)] = [A.index(b) for b in s(a)]
    return WordMorphism(d),A

def balanced_pair_algorithm(s, t=None, w=None, pv=None, pvr=None, r_action=False, getgraph=0, getbp=0, algo="Python", verb=0, stop_event=None):
    """
    Balanced pair algorithm, to test if the subshift of s has pure discrete spectrum,
    from "A generalized balanced pair algorithm" by Brian F. Martensen

    INPUT:
        - ``s`` - WordMorphism -- the substitution
        - ``t`` - WordMorphism (default: ``None``) -- the pre-period
        - ``w`` - Word -- prefix of a periodic point of s
        - ``pv`` - (default: ``None``) - vector or matrix - projection
        - ``pvr`` - (default: ``None``) - length vector in RR
        - ``r_action`` - bool (default: ``False``) -- if True, find if the R-action has pure discrete spectrum
        - ``getgraph`` - bool (default: ``False``) -- if True, return balanced pairs and the graph on balanced pairs, represented with entering edges
        - ``getbp`` - bool (default: ``False``) -- if True, return the set of balanced pairs stable by the susbtitution
        - ``algo`` - str (default: "python") -- algorithm used. "Python" or "C++"
        - ``verb`` - int (default: 0) - If > 0, print informations
        - ``stop_event`` - multiprocessing.Event (default: ``None``) -- used to stop the function

    OUTPUT:
        A bool.

    EXAMPLES::
        sage: from eigenmorphic import *
        sage: s = WordMorphism('a->ab,b->ac,c->a')
        sage: balanced_pair_algorithm(s)
        True
        sage: s = WordMorphism('a->Ab,b->A,A->aB,B->a')
        sage: balanced_pair_algorithm(s)
        False
        sage: s = WordMorphism('1->31,2->412,3->312,4->412')
        sage: balanced_pair_algorithm(s)
        True

        # Example giving wrong answer
        # because the prefix w does not satisfy the condition that w+w[:1] is also a prefix
        sage: s = WordMorphism('a->Ab,b->Ac,c->A,A->aB,B->aC,C->a')
        sage: balanced_pair_algorithm(s)
        False

        # non terminating example from "A generalized balanced pair algorithm" by Brian F. Martensen
        sage: s = WordMorphism('1->1234,2->124,3->13234,4->1324')
        sage: has_pure_discrete_spectrum(s)  # not tested
    """
    # test if the Perron eigenvalue is Pisot
    m = s.incidence_matrix()
    b = max(m.eigenvalues())
    if not is_pisot(b):
        if verb > 0:
            print("Perron eigenvalue is not Pisot.")
        return False
    # convert s and w
    s,A = convert_substitution(s)
    if verb > 1:
        print("s = %s" % s)
        print("A = %s" % A)
    if w is not None:
        w = Word([A.index(a) for a in w], alphabet=s.domain().alphabet())
    # find a power of s that have fixed point
    p = 1
    while (len((s**p).fixed_points()) == 0):
        p += 1
    #s = s**p
    # define w is not
    if w is None:
        w = (s**p).fixed_points()[0][:1]
        if verb > 0:
            print("w = " + str(w))
    # find a power of s such that w is a prefix of a fixed point
    while True:
        try:
            u = (s**p).fixed_point(w[0])
            if u[:len(w)] != w:
                raise ValueError("%s must be the prefix of a periodic point." % w)
        except:
            p += 1
            continue
        break
    # define t if not
    if t is None:
        t = WordMorphism({i:[i] for i in s.domain().alphabet()})
    # define pv if not
    if pv is None:
        m = s.incidence_matrix()
        if verb > 1:
            print("incidence matrix:")
            print(m)
        _, pvr, pv = getV(m)
        if verb > 1:
            print("pv =")
            print(pv)
    if not r_action:
        # test the condition ensuring that coincidences are aligned
        if getB(s, t) != b.minpoly():
            # add vector
            mt = t.incidence_matrix()
            ve = vector([1 for _ in range(pv.ncols())])*mt
            if verb > 0:
                print("Add vector %s to ensure that coincidences are aligned." % ve)
            pv = matrix(list(pv)+[ve])
    # compute the first set of balanced pairs
    to_see = first_balanced_pairs(s**p, w, pv, pvr, verb-1)
    if verb > 1:
        print("first balanced pairs:")
        print(to_see)
    if algo == "C++":
        from eigenmorphic.bpa_c import bpa_c
        bpa_c(s, pv, to_see, verb=verb)
    elif algo != "Python":
        raise ValueError("algo type unknown. Choose between 'Python' or 'C++'.")
    # stabilize by the substitution
    lb = {(u,v):i for i,(u,v) in enumerate(to_see)} # associate an integer to each balanced pair
    n = len(lb)
    ee = dict() # list of entering edges of the graph, for each state, labeled by integers
    while len(to_see) > 0:
        if stop_event is not None and stop_event.is_set():
            return
        u,v = to_see.pop()
        if verb > 2:
            txt1 = "s(" + str(u) + ") = "
            txt2 = " (" + str(v) + ")   "
        for u2,v2 in decompose(s(u), s(v), pv, pvr, verb=verb-3):
            if verb > 2:
                txt1 += "(" + str(u2) + ")"
                txt2 += "(" + str(v2) + ")"
            if (v2, u2) in lb:
                u2, v2 = v2, u2 # swap
            if (u2,v2) not in lb:
                lb[(u2,v2)] = n
                to_see.add((u2,v2))
                n += 1
            if verb > 3:
                print("%s --> %s (%s --> %s)" % (lb[(u,v)], lb[(u2,v2)], (u,v), (u2,v2)))
            if lb[(u2,v2)] not in ee:
                ee[lb[(u2,v2)]] = set()
            ee[lb[(u2,v2)]].add(lb[(u,v)])
        if verb > 2:
            print(txt1)
            print(txt2)
    if verb > 0:
        print("%s balanced pairs" % len(lb))
        if verb > 1:
            print(lb)
        print("max length of balance pair : %s" % max([len(w) for w,_ in lb]))
        print("%s edges" % len(ee))
        if verb > 1:
            print(ee)
    if getgraph:
        return lb, ee
    if getbp:
        return set(lb)
    # browse the graph to determine if every pair leads to a coincidence
    to_see = [lb[(u,v)] for u,v in lb if len(u) == 1 and u == v] # list of coincidences
    seen = set(to_see)
    while len(to_see) > 0:
        e = to_see.pop()
        if e not in ee:
            continue
        for e2 in ee[e]:
            if e2 not in seen:
                seen.add(e2)
                to_see.append(e2)
    pd = len(seen) == len(lb) # pure discreteness
    if verb > 1:
        print("Algo finished !")
    return pd

def check_dimension(s, t, d, verb=0, stop_event=None):
    """
    Check that the set of eigenvalues is big enough to have pure discrete spectrum
    
    INPUT:
        - ``s`` - WordMorphism
        - ``d`` - degree of Perron eigenvalue of s
        - ``verb`` - int (default: ``0``) -- if > 0, print informations
    """
    if d == 1:
        if verb > 0:
            print("Perron eigenvalue is an integer, compute eigenvalues...")
        # compute the set of eigenvalues
        eigs = morphic_eigenvalues(s, t)
        if eigs == ZZ:
            if verb > 0:
                print(" -> weakly mixing thus non purely discrete")
            return False
        try:
            if eigs.d == 1:
                print(" -> finite number of rational eigenvalues thus non purely discrete")
                return False
        except:
            pass
    else:
        # compute the dimension of the Q-vector space generated by eigenvalues
        de = dimension_eigenvalues(s, t)
        if verb > 0:
            print("dimension eigenvalues :", de)
        if de < d:
            if verb > 0:
                print("not enough eigenvalues to have pure discrete spectrum : %s < %s" % (de, d))
            return False
    return True

import multiprocessing, time

def worker(f, args, C, stop_event, result_queue, verb):
    """
    Function used by has_pure_discrete_spectrum() to execute the balanced pair algorithm in parallel with several words
    """
    res = f(*args, stop_event=stop_event)
    if res is not None:
        w = args[2]
        if w in ZZ: # check_dimension
            if res:
                if verb > 0:
                    print("test of eigenvalues terminated but unconclusive")
                return
            else:
                if verb > 0:
                    print("test of eigenvalues terminated conclusively")
                stop_event.set()  # tell to other processes to stop
                result_queue.put(False)  # send result
                return
        # balanced pair algorithm
        if verb > 1:
            print("C(w) =", C*vector(w.abelian_vector()))
        if res or (C*vector(w.abelian_vector())).is_zero():
            if verb > 0:
                print("balanced pair algorithm terminated conclusively with w =", w)
            if not stop_event.is_set():
                stop_event.set()  # tell to other processes to stop
                result_queue.put(res)  # send result
        else:
            if verb > 0:
                print("balanced pair algorithm terminated but unconclusive with w =", w)

def stopper(processes):
    """
    Function used by has_pure_discrete_spectrum() to stop processes
    """
    time.sleep(1) # wait to let time to processes to finish by themsleves
    print(processes)
    for p in processes:
        if p.is_alive():
            p.terminate()  # kill process

def getV(m):
    """
    Return a matrix in ZZ whose right-kernel is the same as the Perron left-eigenvector

    INPUT:
        - m - matrix with rational coefficients

    OUTPUT:
        The Perron number, the Perron eigenvector with float coeffs and a matrix with base_ring ZZ

    EXAMPLES::
        sage: from eigenmorphic.balanced_pair_algo import getV
        sage: s = WordMorphism('a->ab,b->ac,c->a')
        sage: m = s.incidence_matrix()
        sage: getV(m)
        (
        1.839286755214161?, (1.0, 0.8392867552141612, 0.5436890126920764),
        <BLANKLINE>
        [1 0 0]
        [0 1 0]
        [0 0 1]
        )
    """
    b, vp, _ = max(m.eigenvectors_left())
    vp = vp[0]
    K = NumberField(b.minpoly(), 'b', embedding=b)
    vp = vector((K(t) for t in vp))
    m = matrix([list(t) for t in vp]).transpose()
    E = VectorSpace(QQ, m.ncols())
    m = matrix(E.subspace(m).basis())
    d = lcm((c.denom() for c in m.coefficients()))
    return b, vector([float(t) for t in vp]), matrix(m*d, base_ring=ZZ)

def has_pure_discrete_spectrum(s, t=None, nprocs=4, check_dim=True, timeout=None, verb=0):
    """
    Test if the subshift of s has pure discrete spectrum.

    INPUT:
        - ``s`` - WordMorphism -- the substitution (assumed to be primitive)
        - ``t`` - WordMorphism (default: ``None``) -- the pre-period
        - ``nprocs`` - int (default: 4) -- number of words w tested simultaneously
        - ``check_dim`` - bool (default: ``True``) -- if True, test if there are enough eigenvalues to have pure dicrete spectrum. If False, it can return a wrong answer.
        - ``timeout`` - int (default: ``None``) -- timeout in seconds
        - ``verb`` - int (default: ``0``) -- If > 0, print informations

    OUTPUT:
        A bool.

    EXAMPLES::
        sage: from eigenmorphic import *
        sage: s = WordMorphism('a->ab,b->ac,c->a')
        sage: has_pure_discrete_spectrum(s)
        True
        sage: s = WordMorphism('a->Ab,b->A,A->aB,B->a')
        sage: has_pure_discrete_spectrum(s)
        False
        sage: s = WordMorphism('1->31,2->412,3->312,4->412')
        sage: has_pure_discrete_spectrum(s)
        True
        sage: s = WordMorphism('a->Ab,b->Ac,c->A,A->aB,B->aC,C->a')
        sage: has_pure_discrete_spectrum(s)
        True
        
        # example with a pre-period, due to N. Bedaride
        sage: t = WordMorphism('0->02,1->1,2->2,3->0335342,4->0342,5->033535342')
        sage: s = WordMorphism('0->0402,1->012,2->01202,3->04353402,4->043402,5->043553402')
        sage: has_pure_discrete_spectrum(s, t)
        True

        # non terminating example for the balanced pair alogorithm
        # from "A generalized balanced pair algorithm" by Brian F. Martensen
        # the computation of eigenvalues shows it is weakly mixing 
        sage: s = WordMorphism('1->1234,2->124,3->13234,4->1324')
        sage: has_pure_discrete_spectrum(s)
        False
    """
    # test if the Perron eigenvalue is Pisot
    m = s.incidence_matrix()
    b = max(m.eigenvalues())
    if not is_pisot(b):
        if verb > 0:
            print("Perron eigenvalue is not Pisot.")
        return False
    # compute pv
    if verb > 1:
        print("incidence matrix:")
        print(m)
    b, pvr, pv = getV(m)
    if verb > 1:
        print("pv =")
        print(pv)
        print("pvr =", pvr)
    # compute coboundary space, to test condition on word in case of False result
    C = coboundary_basis(s)
    if verb > 1:
        print("coboundary basis:")
        print(C)
        print("A = %s" % s.domain().alphabet())
    # create multiprocessing tools
    stop_event = multiprocessing.Event()  # shared event to indicate to stop
    result_queue = multiprocessing.Queue()  # to get results
    # list of processes
    processes = []
    
    # test the condition ensuring that coincidences are aligned
    if getB(s, t) == b.minpoly():
        if verb > 0:
            print("The condition ensuring that there is enough eigenvalues is satisfied.")
        check_dim = 0 # we already know that there are enough eigenvalues
    
    rt = time.monotonic();
    
    if check_dim:
        if verb > 0:
            print("test if there are enough eigenvalues...")
        #futures[executor.submit(check_dimension, s, b.minpoly().degree(), verb)] = Word([], alphabet=s.domain().alphabet())
        p = multiprocessing.Process(target=worker, args=(check_dimension, (s, t, b.minpoly().degree(), verb), C, stop_event, result_queue, verb))
        pcd = p
        p.start()
        processes.append(p)
    for n in range(1,1000): # browse possible lengths
        if verb > 1:
            print("test with prefixes of length %s" % n)
        sw = set()
        for lw in s.periodic_points():
            for w in lw:
                sw.add(w[:n])
        if verb > 1:
            print(sw)
        for w in sw:
            # submit a new task
            if verb > 0:
                print("execute balanced_pair_algorithm with w = %s..." % w)
            #futures[executor.submit(balanced_pair_algorithm, s, w, pv)] = w
            p = multiprocessing.Process(target=worker, args=(balanced_pair_algorithm, (s, t, w, pv, pvr), C, stop_event, result_queue, verb))
            p.start()
            processes.append(p)
            while len(processes) == nprocs:
                if timeout is not None:
                    t = time.monotonic()
                    if t-rt > timeout:
                        if verb > 1:
                            print(" timeout stop")
                        # indicate to stop
                        stop_event.set()
                        # wait 1s
                        time.sleep(1)
                        for p in processes:
                            p.kill()
                            #p.terminate()
                        return
                # remove processes that terminates
                processes2 = []
                for p in processes:
                    if p.is_alive():
                        processes2.append(p)
                processes = processes2
                # get result and force processes to stop
                if stop_event.is_set():
                    if check_dim:
                        if pcd.is_alive():
                            # wait the test of dimension to terminate
                            if verb > 0:
                                print("Wait the test of eigenvalues...")
                            if timeout:
                                pcd.join(timeout - t + rt)
                            else:
                                pcd.join()
                    for p in processes:
                        p.kill()
                        #p.terminate()
                    return result_queue.get()
                time.sleep(.1)
