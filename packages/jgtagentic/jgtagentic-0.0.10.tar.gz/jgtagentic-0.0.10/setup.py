#!/usr/bin/env Python
"""
jgtagentic
"""

from setuptools import find_packages, setup
import re

#from jgtml import __version__ as version
def read_version():
    with open("jgtagentic/__init__.py") as f:
        content=f.read()
        version_match = re.search(r"version=['\"]([^'\"]*)['\"]", content)
        return version_match.group(1)

version = read_version()

#print(f"Version: {version}")
setup(
    name="jgtagentic",
    version=version,
    description="JGTrading Agentic",
    long_description=open("README.md").read(),
    author="GUillaume Isabelle",
    author_email="jgi@jgwill.com",
    url="https://github.com/jgwill/jgtagentic",
    packages=find_packages(include=["jgtagentic"], exclude=["*test*"]),

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial ",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7.16",
    ],
)
