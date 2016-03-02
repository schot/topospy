#!/usr/bin/env python

from distutils.core import setup

setup(
    name='topos',
    version='0.2',
    description='Pythonic ToPoS library',
    author='Jeroen Schot',
    author_email='jeroen.schot@surfsara.nl',
    url='https://github.com/schot/topospy',
    py_modules=['topos'],
    data_files=[('', ['LICENSE', 'README.rst'])],
    license='Apache 2.0',
    classifiers=(
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    )
)
