from __future__ import print_function
from setuptools import setup
from pip.req import parse_requirements
from os.path import join, dirname, abspath
import re

def get_version_from(file):
    version = re.search(
        '^__version__\s*=\s*\'(.*)\'',
        open(file).read(),
        re.M
    ).group(1)
    return version

version = get_version_from(join(dirname(__file__), 'gaw', '__init__.py'))

setup(
    name = 'gaw',
    packages = ['gaw', 'gaw.jsonsocketserver', 'gaw.postoffice'],
    install_requires=[
        'eventlet'
    ],
    entry_points={},
    version = version,
    description = 'A small library that helps you developing microservices over simple TCP socket with ease',
    author = 'Konpat Preechakul',
    author_email = 'the.akita.ta@gmail.com',
    url = 'https://github.com/phizaz/gaw', # use the URL to the github repo
    keywords = ['microservice'] , # arbitrary keywords
    classifiers = [],
)