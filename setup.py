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
        'munch==2.5.0',
        'python-telegram-bot==20.2',
        'peewee==3.16.0',
        'pytest==8.2.2',
        'freezegun==1.5.1',
    ],
    test_suite='tests'
)
