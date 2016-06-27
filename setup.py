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

version = get_version_from(join(dirname(__file__), 'microservice_tools', '__init__.py'))

setup(
    name = 'microservice_tools',
    packages = ['microservice_tools'],
    install_requires=[
        'eventlet'
    ],
    entry_points={},
    version = version,
    description = 'Global memory micro-webservice with REST interface for multi-node parallelism',
    author = 'Konpat Preechakul',
    author_email = 'the.akita.ta@gmail.com',
    url = 'https://github.com/phizaz/microservice_tools', # use the URL to the github repo
    keywords = ['cache'], # arbitrary keywords
    classifiers = [],
)