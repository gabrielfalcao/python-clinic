#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""An archetypical service mock for an ideal shipment
provider that implements the adapter interface
"""
import codecs
from pathlib import Path
from setuptools import setup, find_packages


local_file = lambda f: codecs.open(str(Path(__file__).parent.joinpath(f)), 'r', 'utf-8').read()


def read_version():
    scope = {}
    exec(local_file('python_clinic/version.py'), scope)
    return scope.pop('version')


def read_requirements():
    return local_file('requirements.txt').splitlines()


def read_readme():
    """Read README content.
    If the README.rst file does not exist yet
    (this is the case when not releasing)
    only the short description is returned.
    """
    try:
        return local_file('README.rst')
    except IOError:
        return __doc__


DATA_EXTENSIONS = ' '.join([
    '*.cfg',
    '*.css',
    '*.html',
    '*.js',
    '*.json',
    '*.map',
    '*.rst',
    '*.txt',
    '*.yaml',
    '*.yml',
    '*.png',
])

setup(
    author='Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    description=read_version(),
    include_package_data=True,
    install_requires=read_requirements(),
    long_description=read_readme(),
    name='python-clinic',
    packages=find_packages(exclude=['*tests*']),
    test_suite='nose.collector',
    version=read_version(),
    entry_points={
        'console_scripts': ['python-clinic = python_clinic.console:entrypoint'],
    },
    package_data=dict([
        ('python_clinic', DATA_EXTENSIONS),
        ('python_clinic.web.ui', DATA_EXTENSIONS),
        ('python_clinic.web.schemas.adapter', '*.json'),
        ('python_clinic.web.schemas.provider', '*.json'),
    ]),
    zip_safe=False,
)
