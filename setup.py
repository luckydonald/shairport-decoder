# -*- coding: utf-8 -*-
__author__ = 'luckydonald'

from setuptools import setup, find_packages # Always prefer setuptools over distutils
from codecs import open # To use a consistent encoding
from os import path
here = path.abspath(path.dirname(__file__))
from shairportdecoder import VERSION

long_description = """A Python module that parses the metadata and status information provided by shairport-sync."""
short_description = "Read Metadata and status from Shairport Sync."
setup(
	name='shairportdecoder',
	version=VERSION,
	description=short_description,
	long_description=long_description,
	# The project's main homepage.
	url='https://github.com/luckydonald/shairportdecoder',
	# Author details
	author='luckydonald',
	author_email='code@luckydonald.de',
	# Choose your license
	license='GPLv3+',
	# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
	'Development Status :: 4 - Beta', # 3 - Alpha, 4 - Beta, 5 - Production/Stable
	# Indicate who your project is intended for
	'Intended Audience :: Developers',
	'Topic :: Software Development :: Build Tools',
	# Pick your license as you wish (should match "license" above)
	'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
	# Specify the Python versions you support here. In particular, ensure
	# that you indicate whether you support Python 2, Python 3 or both.
	# 'Programming Language :: Python :: 2',
	# 'Programming Language :: Python :: 2.6',
	# 'Programming Language :: Python :: 2.7',
	'Programming Language :: Python',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.2',
	'Programming Language :: Python :: 3.3',
	'Programming Language :: Python :: 3.4',
	'Operating System :: Unix',
	'Operating System :: POSIX', # is it?
	'Operating System :: MacOS :: MacOS X',
	'Topic :: Multimedia',
	'Topic :: Multimedia :: Sound/Audio',  # there are no good tags :(
	'Topic :: Multimedia :: Sound/Audio :: Analysis',  # because metadata???
	'Topic :: Software Development :: Libraries'
	'Topic :: Utilities'
	],
	# What does your project relate to?
	keywords='python music airplay shairplay dmap daap music mp3 remote meta metadata display',
	# You can just specify the packages manually here if your project is
	# simple. Or you can use find_packages().
	packages= ['shairportdecoder', 'shairportdecoder.remote'], #find_packages(exclude=['contrib', 'docs', 'tests*']),
	# List run-time dependencies here. These will be installed by pip when your
	# project is installed. For an analysis of "install_requires" vs pip's
	# requirements files see:
	# https://packaging.python.org/en/latest/requirements.html
	install_requires=["DictObject>=0.1.1", "luckydonald-utils>=0.18","requests"]
	# List additional groups of dependencies here (e.g. development dependencies).
	# You can install these using the following syntax, for example:
	# $ pip install -e .[dev,test]
	#extras_require = {
	#'dev': ['check-manifest'],
	#'test': ['coverage'],
	#},
	# If there are data files included in your packages that need to be
	# installed, specify them here. If using Python 2.6 or less, then these
	# have to be included in MANIFEST.in as well.
	#package_data={
	#'sample': ['package_data.dat'],
	#},
	# Although 'package_data' is the preferred approach, in some case you may
	# need to place data files outside of your packages.
	# see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
	# In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
	#data_files=[('my_data', ['data/data_file'])],
	# To provide executable scripts, use entry points in preference to the
	# "scripts" keyword. Entry points provide cross-platform support and allow
	# pip to create the appropriate form of executable for the target platform.
)
