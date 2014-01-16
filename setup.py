#!/usr/bin/python2.6

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "oscmd",
    version = "0.0.3",
    author = "Fabrice Bacchella",
    author_email = "fabrice.bacchella@3ds.com",
    description = "Command line tool to manage VM hosted by Outscale.",
    license = "Apache",
    keywords = "CLI Outscale VM AWS",
    install_requires=[
        'boto', 'PyYAML',
    ],
    url = "https://github.com/fbacchella/oscmd/",
    packages=['oslib', 'oslib.ami', 'oslib.eip', 'oslib.instance', 'oslib.volume', 'oslib.snapshot', 'oslib.securitygroup', 'oslib.keypair', 'oslib.resources' ],
    package_data = {"oslib.resources": ["*"] },
    scripts=['oscmd'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Classifier: Operating System :: OS Independent",
        "Environment :: Console",
        "Programming Language :: Python :: 2",
    ],
    platforms=["Posix", "MacOS X", "Windows"],
)
