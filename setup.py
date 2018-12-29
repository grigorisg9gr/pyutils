from setuptools import setup, find_packages
import numpy as np


setup(name='research_pyutils',
      version='0.2',
      description='Utilities for my research.',
      author='Grigorios Chrysos',
      author_email='grigoris.chrysos@gmail.com',
      include_dirs=[np.get_include()],
      packages=find_packages()
)
