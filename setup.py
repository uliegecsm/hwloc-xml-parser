from setuptools import setup

from mypyc.build import mypycify

setup(
    ext_modules = mypycify(
        [
            'hwloc_xml_parser/topology.py',
        ],
        verbose = True,
    ),
)
