# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

from setuptools import setup, find_packages
from web_resource_command import WebResourceCommand

with open('sciit/man/VERSION', 'rb') as f:
    version = f.read().decode('utf-8')

with open('README.md', 'rb') as f:
    long_descr = f.read().decode('utf-8')

with open('requirements.txt', 'rb') as f:
    requirements = f.read().decode('utf-8').split('\n')


setup(
    name='sciit',
    packages=find_packages(),
    install_requires=requirements,
    tests_require=['pytest', ],
    setup_requires=['pytest', 'requests'],
    entry_points={
        'console_scripts': ['git-sciit = sciit.cli.start:main']
    },
    zip_safe=False,
    include_package_data=True,
    version=version,
    description='An application that allow issues to be managed within a version control repository rather than as a '
                'separate database. Contains a command line application that can manage issues.',
    long_description=long_descr,
    author='Nystrom Johann Edwards',
    author_email='nystrom.edwards@gmail.com',
    url='https://gitlab.com/sciit/sciit',
    cmdclass={
        'install_wr': WebResourceCommand
    }
)
