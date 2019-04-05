# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='dialogflow_utils',
    version='0.0.1',
    description='Python Library to automate intent and entity creation in Dialogflow',
    author='Dimitri Henkel',
    author_email='dimitri.henkel@gmail.com',
    packages=find_packages(exclude=('test', 'doc'))
)
