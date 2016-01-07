#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

requirements = [
    'readability-lxml', 'flask-restful', 'flask', 'requests', 'paste', 'cherrypy', 'redis', 'hiredis', 'spooky', 'lxml',
    'cssselect', 'beautifulsoup4', 'langid', 'numpy', 'pattern', 'future', 'webassets', 'pyScss', 'enum34', 'jsmin',
    'csscompressor', 'arrow', 'python-dateutil'
]

setup_requires = [
    'setuptools_git', 'setuptools', 'twine', 'wheel', 'pip', 'nose'
]

name = 'quiet-reading'
version = '0.1'
description = 'clean articles from the web into an easy quiet ad-free reading experience'
author = 'Stephane Martin',
author_email = 'stephane.martin_github@vesperal.eu',
url = 'https://github.com/stephane-martin/quiet-reading',
licens = "LGPLv3+"
keywords = 'python web readability'
data_files = []
test_requirements = []

classifiers = [
    'Development Status   :: 3 - Alpha',
    'Environment          :: Plugins',
    'Environment          :: Web Environment',
    'Environment          :: Console',
    'License              :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    'Programming Language :: Python :: 2.7',
    'Operating System     :: POSIX',
    'Operating System     :: Microsoft :: Windows'
]

entry_points = {
    'console_scripts': [
        'wgetq          = quiet.wgetq:main'
    ]
}

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

long_description = readme + '\n\n' + history


def runsetup():

    setup(
        name=name,
        version=version,
        description=description,
        long_description=long_description,
        author=author,
        author_email=author_email,
        url=url,
        packages=find_packages(exclude=['tests']),
        setup_requires=setup_requires,
        include_package_data=True,
        install_requires=requirements,
        license=licens,
        zip_safe=False,
        keywords=keywords,
        classifiers=classifiers,
        entry_points=entry_points,
        data_files=data_files,
        test_suite='tests',
        tests_require=test_requirements,
    )


if __name__ == "__main__":
    runsetup()
