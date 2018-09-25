# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_descr = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().split('\n')

version = '1.0'

setup(
    name='sciit',
    packages=find_packages(),
    install_requires=requirements,
    tests_require=['nose', ],
    entry_points={
        'console_scripts': ['git-sciit = sciit.cli.start:main']
    },
    zip_safe=False,
    version=version,
    description='An application that allow issues to be managed'
    'within a version control repository rather than'
    'as a separate database.'
    'Contains a command line application that can manage'
    'issues.',
    long_description=long_descr,
    author='Nystrom Johann Edwards',
    author_email='nystrom.edwards@gmail.com',
    url='https://gitlab.com/nystrome/sciit',
)
