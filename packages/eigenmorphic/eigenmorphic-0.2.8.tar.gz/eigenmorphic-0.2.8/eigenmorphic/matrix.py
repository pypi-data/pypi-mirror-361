### correct a problem with matrix
from sage.matrix.constructor import matrix as matrix3
global matrix

def get_sage_version():
	from sage.misc.banner import version
	txt = version()
	while txt[0] not in [str(i) for i in range(10)]+['.']:
		txt = txt[1:]
	i = 0
	while txt[i] in [str(i) for i in range(10)]+['.']:
		i += 1
	txt = txt[:i]
	return float(txt)

def matrix2(m, base_ring=None, ncols=None):
	return matrix3(m, ring=base_ring, ncols=ncols)

if get_sage_version() < 10:
	matrix = matrix2
else:
    matrix = matrix3
###

