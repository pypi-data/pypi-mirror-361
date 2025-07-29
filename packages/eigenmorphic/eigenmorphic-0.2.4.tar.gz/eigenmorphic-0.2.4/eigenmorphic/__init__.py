from sage.misc.lazy_import import lazy_import

### correct a problem with matrix
from sage.matrix.constructor import matrix
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

def matrix2(m, base_ring=None):
	return matrix(m, ring=base_ring)

if get_sage_version() < 10:
	matrix = matrix2
###

lazy_import('eigenmorphic.eigenvalues', ['morphic_eigenvalues', 'dimension_eigenvalues'])

lazy_import('eigenmorphic.coboundary', ['coboundary_basis', 'return_substitution', 'coboundary_graph', 'graph_basis'])

lazy_import('eigenmorphic.IET', ['rauzy_loop_substitution', 'orbit', 'convert_IET', 'anosov_fixed_points', 'plot_surface_with_fixed_pts', 'plot_bratteli', 'graph_of_graphs'])

lazy_import('eigenmorphic.rauzy_fractal', ['usual_projection', 'rauzy_fractal_plot'])

lazy_import('eigenmorphic.balanced_pair_algo', ['return_words', 'proprify', 'balanced_pair_algorithm', 'has_pure_discrete_spectrum'])

lazy_import('eigenmorphic.recognizability', ['is_recognizable'])

