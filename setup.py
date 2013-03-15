#!/usr/bin/env python

import setuptools
import sys

requiredList = ['requests', 'python-dateutil']

if sys.version_info[:2] <= (2, 6):
    requiredList.extend(['argparse', 'unittest2'])
if sys.version_info[:2] <= (2, 7):
    requiredList.extend(['mock'])
if sys.version_info[:2] <= (3,):
    requiredList.extend([])

setuptools.setup(
    name='Troz',
    version='1.0',
    description='The Wizard Of Troz',
    author='Peter Naudus',
    author_email='linuxlefty@fastmail.fm',
    url='http://TheTroz.com',
    packages=setuptools.find_packages(),
    scripts = ['troz.py'],
    install_requires=requiredList,
    extras_require = {
        'docs': ['sphinx', 'sphinxjp.themecore']
    }
)
