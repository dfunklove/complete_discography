#!/usr/bin/env python

from setuptools import setup

setup(name='complete_discography',
    version='1.0',
    author='Daniel Lovette',
    author_email='dfunklove@gmail.com',
    url='https://github.com/dfunklove/complete_discography',
    license='LICENSE.txt',
    description='Complete Discography is a web application which provides a discography for an artist including their aliases and all the groups they performed in.  The data comes from Discogs.com.',
    long_description=open('README.md').read(),
    packages=['complete_discography'],
    scripts=['complete_discography/bin/disco.py', 'complete_discography/bin/disco_server.py'],
    install_requires=['bs4', 'cloudscraper', 'eventlet', 'flask', 'flask_socketio', 'lxml', 'requests', 'requests_toolbelt']
    )
