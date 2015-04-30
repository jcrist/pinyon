from setuptools import setup

setup(name='pinyon',
      version='0.0',
      description=('A library for matching, rewriting, and manipulating '
                     'tree like terms, in pure Python'),
      packages=['pinyon', 'pinyon.matching', 'pinyon.term'],
      author='Jim Crist',
      tests_require=['pytest'],
)
