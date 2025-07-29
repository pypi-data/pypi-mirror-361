#!/usr/bin/env python
import setuptools
from setuptools import find_packages
from numpy.distutils.core import setup
from numpy.distutils.core import Extension
from numpy.distutils import log
from numpy.distutils.command.build_ext import build_ext
import os

plugin_name = 'taurex_ggchem'


packages = find_packages(exclude=('tests', 'doc'))
provides = [plugin_name, ]


requires = []
FORCE_COMPILER = os.environ.get('FORCE_COMPILER', None)
EXTRA_LINK_FLAGS = os.environ.get('EXTRA_LINK_FLAGS', None)

install_requires = []

install_requires = ['numpy',
                    'taurex']


def build_fortran(subpackage,package_name, fortran_sources, extra_compile_args=None, extra_link_args=None):
    ext = Extension(name='.'.join((plugin_name,subpackage,package_name)),
                    extra_compile_args=extra_compile_args,
                    extra_link_args=extra_link_args,
                    extra_f90_compile_args=extra_compile_args,
                    extra_f77_compile_args=extra_compile_args,
                    sources=fortran_sources)

    return ext

def build_libs():
    import platform
    sources = [         
                        

                        
                        'src16/database.f',
                        'src16/is_nan.F',
                        'src16/nasa_polynomial.f',
                        'src16/ggchem.f',
                        'src16/gauss16.f',
                        'src16/gauss8.f',
                        'src16/gauss_nm.f',
                        'src16/massfrac.f',
                        'src16/linpack_q.f90',
                        'src16/slatec_routines.f',
                        'src16/smchem16.f',
                        'src16/smchem8.f',
                        'src16/supersat.f',
                        'src16/stindex.f',
                        'src16/upper.f',
                        'src16/nucleation.f',
                        'src16/equil_cond.f',
                        'taurex_ggchem/glue/init_dustchem_taurex.f',
                        'taurex_ggchem/glue/datamod.f90',
                        'taurex_ggchem/glue/taurex_glue.f90',
                        'taurex_ggchem/glue/taurex_glue.pyf',
                        ]

    compile_args=['-fdefault-real-8', '-fdefault-double-8','-O3']
    link_args=[]
    sysname = platform.system()
    if sysname == "Darwin":
        compile_args.append("-mmacosx-version-min=10.9")
        link_args+= ["-mmacosx-version-min=10.9",]
    if EXTRA_LINK_FLAGS:
        link_args.append(EXTRA_LINK_FLAGS)

    return build_fortran('external', 'fort_ggchem', sources,extra_compile_args=compile_args, 
                         extra_link_args=link_args)
import glob


entry_points = {'taurex.plugins': 'ggchem = taurex_ggchem'}

class _custom_buildext(build_ext):

    def run(self):
        self.compiler = FORCE_COMPILER
        super().run()

extensions = [build_libs(), ]

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

pos = long_description.find('# TauREx')

long_description = long_description[pos:]

version = "1.0.0-dev0"

setup(name=plugin_name,
      author='Ahmed Faris Al-Refaie',
      author_email='ahmed.al-refaie.12@ucl.ac.uk',
      license="BSD",
      description='Python Wrapper for GGchem chemical scheme',
      packages=packages,
      include_package_data=True,
      entry_points=entry_points,
      provides=provides,
      requires=requires,
      version=version,
      keywords=['exoplanet',
                'chemistry'
                'taurex',
                'plugin',
                'taurex3',
                'atmosphere',
                'atmospheric'],
      long_description=long_description,
      install_requires=install_requires,
      ext_modules=extensions,
      long_description_content_type='text/markdown',
      cmdclass={'build_ext': _custom_buildext},
      package_data={plugin_name:['external/data/**']},

      )