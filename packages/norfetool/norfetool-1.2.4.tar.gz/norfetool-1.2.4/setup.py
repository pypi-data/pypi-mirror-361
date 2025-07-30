#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='norfetool',
    version="1.2.4",
    description=(
        "Enhanced figure customization by adding a dedicated algorithm to adjust colorbar tick directions and styles, enabling inward or outward ticks with configurable length and width. This complements existing tools for SCI figure creation using PIL and pkl files, and further simplifies plt style settings. Also improved Slurm script management with flexible base file content replacement."
    ),
    # long_description=open('README.rst').read(),
    author='norfe',
    author_email='21121598@bjtu.edu.cn',
    maintainer='norfe',
    maintainer_email='21121598@bjtu.edu.cn',
    license='BSD License',
    packages=find_packages(),
    # py_modules=["norfetools"],
    platforms=["all"],
    url='https://github.com/liftes/PythonDraw',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'matplotlib',
        'numpy',
    ]
)

# twine upload -u __token__ -p pypi-token dist/*