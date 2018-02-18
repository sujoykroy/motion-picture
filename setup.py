"""Setup for img2vid
"""

from setuptools import setup, find_packages

import codecs
import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with codecs.open(os.path.join(THIS_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requirements = []
for line in codecs.open(os.path.join(THIS_DIR, 'requirements.txt'), encoding='utf-8'):
    if line.strip() and not line.startswith('#'):
        requirements.append(line)

setup(
    name='img2vid',
    version='0.1.0.dev1',
    description = 'Application to make video from images and other media',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=requirements,
    entry_points={
        'console_scripts':[
            'img2vid=img2vid:main'
        ]
    },
    test_suite='tests.test_all',
    package_data={
        'img2vid': ['configs/*.ini']
    }
)
