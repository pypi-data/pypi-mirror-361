from sage.misc.lazy_import import lazy_import

lazy_import('eigenmorphic.eigenvalues', ['morphic_eigenvalues', 'dimension_eigenvalues'])

lazy_import('eigenmorphic.coboundary', ['coboundary_basis', 'return_substitution', 'coboundary_graph', 'graph_basis'])

lazy_import('eigenmorphic.IET', ['rauzy_loop_substitution', 'orbit', 'convert_IET', 'anosov_fixed_points', 'plot_surface_with_fixed_pts', 'plot_bratteli', 'graph_of_graphs'])

lazy_import('eigenmorphic.rauzy_fractal', ['usual_projection', 'rauzy_fractal_plot'])

lazy_import('eigenmorphic.balanced_pair_algo', ['return_words', 'proprify', 'balanced_pair_algorithm', 'has_pure_discrete_spectrum'])

lazy_import('eigenmorphic.recognizability', ['is_recognizable'])

