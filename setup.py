#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from polytester import __name__ as package_name

DESCRIPTION = "A simple, easy-to-use multi-language test runner."
ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)
VERSION = "1.2.3"

reqs = []
with open("requirements.txt", "r+") as f:
    for line in f.readlines():
        reqs.append(line.strip())

try:
    import os
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
except:
    long_description = DESCRIPTION + '\n'

setup(
    name=package_name,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Steven Skoczen",
    author_email="skoczen@gmail.com",
    url="https://github.com/skoczen/polytester",
    version=VERSION,
    download_url=f"https://github.com/skoczen/polytester/archive/refs/tags/{VERSION}.tar.gz",
    install_requires=reqs,
    packages=find_packages(),
    include_package_data=True,
    keywords=["test", "multi-language", "nose", "karma", "jasmine", "rails", "runner", "junit", "pytest"],
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        'console_scripts': ['pt = polytester.main:main', 'polytester = polytester.main:main'],
    },
)
