#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from pysblibs import __version__ as version

with open('README.md') as f:
    long_description = f.read()

# Setting up
setup(
    name="pysblibs",
    version=version,
    author="Lyudmil Vladimirov",
    author_email="lyu@sensorbase.io",
    maintainer="Sensorbase",
    url='TODO',
    description='Python Sensorbase Libraries',
    long_description=long_description,
    long_description_content_type='text/markdown',
    project_urls={
        'Documentation': 'TODO',
        'Source': 'TODO',
        'Issue Tracker': 'TODO'
    },
    packages=find_packages(exclude=('docs', '*.tests')),
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
    install_requires=['numpy', 'paho-mqtt', 'asyncio', 'netifaces', 'setuptools>=42'],
    extras_require={
        'dev': ['pytest-flake8', 'pytest-cov', 'flake8<5', 'sphinx', 'sphinx_rtd_theme',
                'sphinx-gallery>=0.8'],
        'madoka': ['pymadoka'],
    },
    python_requires='>=3.7',
    keywords=['python'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ]
)
