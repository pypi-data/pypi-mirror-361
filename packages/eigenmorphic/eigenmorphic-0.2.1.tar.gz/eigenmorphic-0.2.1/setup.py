## -*- encoding: utf-8 -*-
import os
import sys
from setuptools import setup
from codecs import open # To open the README file with proper encoding
#from setuptools.command.test import test as TestCommand # for tests
from distutils.command.build_ext import build_ext as _build_ext

from setuptools.extension import Extension

# Get information from separate files (README, VERSION)
def readfile(filename):
    with open(filename,  encoding='utf-8') as f:
        return f.read()

class build_ext(_build_ext):
    def finalize_options(self):
        import subprocess
        from Cython.Build import cythonize
        import json

        # run the configure script
        subprocess.check_call(["make", "configure"])
        try:
            subprocess.check_call(["sh", "./configure"])
        except subprocess.CalledProcessError:
            subprocess.check_call(["cat", "config.log"])

        # configure created config.json that we can no read
        config = json.load(open("./config.json"))

        self.distribution.ext_modules[:] = cythonize(
            self.distribution.ext_modules, include_path=sys.path)
        _build_ext.finalize_options(self)

# For the tests
#class SageTest(TestCommand):
#    def run_tests(self):
#        errno = os.system("sage -t --force-lib eigenmorphic")
#        if errno != 0:
#            sys.exit(1)

setup(
    name = "eigenmorphic",
    version = readfile("VERSION"), # the VERSION file is shared with the documentation
    description='Eigenvalues of morphic subshifts',
    long_description = readfile("README.md"), # get the long description from the README
    long_description_content_type = 'text/markdown',
    url='https://gitlab.com/mercatp/eigenmorphic',
    author='Paul Mercat',
    author_email='paul.mercat@univ-amu.fr', # choose a main contact email
    license='GPLv3.0', # This should be consistent with the LICENCE file
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'Topic :: Software Development :: Build Tools',
      'Topic :: Scientific/Engineering :: Mathematics',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Programming Language :: Python :: 2.7',
    ], # classifiers list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords = "SageMath Eigenvalue Substitutive Morphic Subshift",
    packages = ['eigenmorphic']
    #cmdclass = { 'test': SageTest}, # adding a special setup command for tests
)
