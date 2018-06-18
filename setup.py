# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import subprocess
from setuptools import setup, find_packages


version = subprocess.run(['git', 'tag'], stdout=subprocess.PIPE)
version = version.stdout.decode('utf-8')
doc = open('gitissue/man/VERSION', 'w')
doc.write(version)
doc.close()

with open('README.md', 'rb') as f:
    long_descr = f.read().decode('utf-8')


setup(
    name='git-issue',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['git-issue = gitissue.cli.start:main']
    },
    zip_safe=True,
    include_package_data=True,
    version=version,
    description='Python command line application bare bones template.',
    long_description=long_descr,
    author='Nystrom Johann Edwards',
    author_email='nystrom.edwards@gmail.com',
    url='https://gitlab.com/nystrome/source-issue-tracker',
)
