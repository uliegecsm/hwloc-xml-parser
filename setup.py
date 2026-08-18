from mypyc.build import mypycify
from setuptools import setup

setup(
    ext_modules = mypycify(
        [
            'hwloc_xml_parser/topology.py',
        ],
        verbose = True,
    ),
)
