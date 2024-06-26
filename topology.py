import dataclasses
import pathlib
import subprocess
import tempfile
import typing
import xml.etree
import xml.etree.ElementTree

import typeguard

@dataclasses.dataclass(frozen = False)
class Object:
    """
    Base class for objects (Package, Core, PU, ...) that `hwloc` organizes in a tree.

    References:
        * https://hwloc.readthedocs.io/en/stable/termsanddefs.html
    """
    os_index           : int = -1
    hierarchical_index : str = ''
    logical_index      : int = -1

    @classmethod
    @typeguard.typechecked
    def get_logical_from_physical(cls, type : str, hierarchical_indices : typing.List[str]) -> typing.List[int]:
        """
        Method to convert from an OS index (physical index) that the OS assigns to an object to the logical
        index that `hwloc` assigns to this object.
        """
        args = [
            'hwloc-calc', '-I', type, '--physical-input', '--logical-output', *hierarchical_indices,
        ]
        return [int(x) for x in subprocess.check_output(args = args).decode().strip().split(',')]

class PU(Object):
    """
    Processing unit. The smallest unit of computation represented by `hwloc`.
    """
    @typeguard.typechecked
    def __init__(self, element : xml.etree.ElementTree.Element, parent : 'Core') -> None:
        self.parent = parent
        self.type = 'PU'
        self.os_index = int(element.attrib['os_index'])
        self.hierarchical_index = f'{parent.parent.type}:{parent.parent.os_index}.{parent.type}:{parent.os_index}.PU:{self.os_index}'

class Core(Object):
    """
    Core.
    """
    @typeguard.typechecked
    def __init__(self, element : xml.etree.ElementTree.Element, parent : 'Package') -> None:
        self.parent = parent
        self.type = 'Core'
        self.os_index = int(element.attrib['os_index'])
        self.hierarchical_index = f'{parent.type}:{parent.os_index}.{self.type}:{self.os_index}'
        self.pus = [PU(x, parent = self) for x in element.findall(path = "object[@type='PU']")]

class Package(Object):
    """
    Package. Usually equivalent to a socket.
    """
    @typeguard.typechecked
    def __init__(self, element : xml.etree.ElementTree.Element) -> None:
        self.type = 'Package'
        self.os_index = int(element.attrib['os_index'])
        self.hierarchical_index = f'Package:{self.os_index}'
        self.cores = [Core(x, parent = self) for x in element.findall(path = "object[@type='Core']")]

class SystemTopology:
    """
    Read the system topology as reported by `hwloc`'s tool `lstopo`.

    References:
        * https://hwloc.readthedocs.io/en/stable/tools.html#cli_lstopo
    """
    @typeguard.typechecked
    def __init__(self, load : bool = True, caches : bool = False, io : bool = False, bridges : bool = False) -> None:
        """
        Initialize with optional load of the the system topology from `lstopo-no-graphics`.
        """
        if load: self._load(caches = caches, io = io, bridges = bridges)

    @typeguard.typechecked
    def _load(self, caches : bool = False, io : bool = False, bridges : bool = False) -> None:
        """
        Initialize the system topology from `lstopo-no-graphics`.
        """
        cmd = ['lstopo-no-graphics', '--no-collapse']

        if not caches : cmd.append('--no-caches')
        if not io     : cmd.append('--no-io')
        if not bridges: cmd.append('--no-bridges')

        with tempfile.NamedTemporaryFile(mode = 'w+', suffix = '.xml') as filename:

            cmd.append('--force')
            cmd.append(filename.name)

            subprocess.check_call(args = cmd)

            self._parse(filename = filename.name)

    @typeguard.typechecked
    def _parse(self, filename : typing.Union[pathlib.Path, str]) -> None:
        """
        Parse output of `lstopo-no-graphics`.
        """
        self.lstopo = xml.etree.ElementTree.parse(source = filename)

        self.topology = self.lstopo.getroot()

        # The root node is the 'topology'.
        if not self.topology.tag == 'topology':
            raise ValueError(f"Expected 'topology' tag, got '{self.topology.tag}'")

        # It has several children, among them the 'Machine' object
        if not len(self.topology.findall(path = 'object[@type=\'Machine\']')) == 1:
            raise ValueError("Expected a single 'Machine' object")

        self.machine = self.topology.find(path = 'object[@type=\'Machine\']')

        if not self.machine.tag == 'object':
            raise ValueError(f"Expected 'object' tag, got '{self.machine.tag}'")
        
        if not self.machine.attrib['type'] == 'Machine':
            raise ValueError(f"Expected 'Machine' type, got '{self.machine.attrib['type']}'")

        # The 'Machine' object has many 'info' children. Its 'object' children are the 'Package's.
        if not all(x.tag in ['info', 'object'] for x in self.machine):
            raise ValueError("Expected 'info' and 'object' children of 'Machine' object")

        # Parse all the packages and their children.
        self.packages = [Package(x) for x in self.machine.findall(path = 'object[@type=\'Package\']')]

        # Set the logical indices for the packages, cores, and PUs.
        for objects in [self.packages, list(self.recurse_cores()), list(self.recurse_pus())]:
            logical_indices = Object.get_logical_from_physical(
            type = objects[0].type,
            hierarchical_indices = [obj.hierarchical_index for obj in objects]
        )

        for obj, logical_index in zip(objects, logical_indices):
            obj.logical_index = logical_index

    @typeguard.typechecked
    def __str__(self) -> str:
        """
        Returns a string representation of the system topology.
        """
        descr = ''
        for package in self.packages:
            descr += f'{package}\n'
            for core in package.cores:
                descr += f'\t{core}\n'
                for pu in core.pus:
                    descr += f'\t\t{pu}\n'
        return descr

    @typeguard.typechecked
    def recurse_cores(self) -> typing.Generator:
        """
        Returns a generator to recurse over all cores.
        """
        for package in self.packages:
            for core in package.cores:
                yield core

    @typeguard.typechecked
    def recurse_pus(self) -> typing.Generator:
        """
        Returns a generator to recurse over all processing units.
        """
        for core in self.recurse_cores():
            for pu in core.pus:
                yield pu
