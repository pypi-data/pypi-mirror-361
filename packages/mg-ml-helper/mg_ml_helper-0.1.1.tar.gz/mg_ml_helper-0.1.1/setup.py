from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='mg_ml_helper',
    version='0.1.1',
    author='Ganesh Gaikwad',
    packages=find_packages(),
    install_requires=[
    ],

    long_description=long_description,
    long_description_content_type='text/markdown',
)