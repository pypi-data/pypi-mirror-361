from setuptools import setup, find_packages

setup(
    name='postprocessing_seismo_lib',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[],
    author='Ryan Tam',
    author_email='rwtam@caltech.edu',
    description='A library for building and parsing Seismology API message bodies.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://scsngit.gps.caltech.edu/services/associator',  # Optional
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
