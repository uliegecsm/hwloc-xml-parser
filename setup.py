from setuptools import setup, find_packages

setup(
    name             = 'hwloc-xml-parser',
    version          = '0.1',
    install_requires = [
        'typeguard',
    ],
    packages         = find_packages(),
    license          = 'MIT',
    url              = 'https://github.com/uliegecsm/hwloc-xml-parser'
)
