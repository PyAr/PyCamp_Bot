#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(
    name='PyCamp_Bot',
    version='3.0',
    description='Bot de telegram para organizar pycamp',
    author='Pyar',
    author_email='pyar@pyar.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'munch==2.1.1',
        'python-telegram-bot==10.0.2',
        'peewee',
    ],
    test_suite='tests'
)
