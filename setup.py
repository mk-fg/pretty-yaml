#!/usr/bin/env python

from setuptools import setup, find_packages
import os, io

pkg_root = os.path.dirname(__file__)

# Error-handling here is to allow package to be built w/o README included
try: readme = io.open(os.path.join(pkg_root, 'README.rst'), encoding='utf-8').read()
except IOError: readme = ''

setup(

	name = 'pyaml',
	version = '17.7.2',
	author = 'Mike Kazantsev',
	author_email = 'mk.fraggod@gmail.com',
	license = 'WTFPL',
	keywords = 'yaml serialization pretty print format human readable readability',
	url = 'https://github.com/mk-fg/pretty-yaml',

	description = 'PyYAML-based module to'
		' produce pretty and readable YAML-serialized data',
	long_description = readme,

	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.5',
		'Topic :: Software Development',
		'Topic :: Software Development :: Libraries :: Python Modules' ],

	install_requires = ['PyYAML'],
	packages = find_packages(),
	package_data = {'': ['README.txt']},
	exclude_package_data = {'': ['README.*']} )
