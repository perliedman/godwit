#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='godwit',
      version=version,
      description='Minimalistic database migration tool',
      author='Per Liedman',
      author_email='per.liedman@kartena.se',
      requires=['psycopg2'],
      packages=['Godwit'],
      license='BSD')