# version 1.0.0

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='movie-link-scrape',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4==4.13.4',
        'selenium==4.34.2'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)