#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='approvaltools',
    version='0.1.0',
    author='Emily Bache',
    author_email='emily@bacheconsulting.com',
    maintainer='Emily Bache',
    maintainer_email='emily@bacheconsulting.com',
    license='MIT',
    url='https://github.com/emilybache/approvaltools',
    description='Useful scripts to use with approval testing',
    long_description=read('README.md'),
    py_modules=['approvaltools'],
    python_requires='>=3.7',
    install_requires=['pytest>=3.5.0', 'approvaltests', 'pytest-approvaltests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'approveall = approveall',
        ],
    },
)
