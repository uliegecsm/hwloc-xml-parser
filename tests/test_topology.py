import subprocess
import unittest
from unittest.mock import call

from topology import SystemTopology

class TestSystemTopology:
    """
        Test :py:class:`system.SystemTopology`.
    """

    def test_parse(self):
        """
        The test reads an `xml` file with the output of `lstopo-no-graphics`
        for a system with the following topology:

        .. code-block:: python

            Package(os_index=0, logical_index=0)
            Core(os_index=0, logical_index=0)
                PU(os_index=0, logical_index=0)
                PU(os_index=4, logical_index=1)
            Core(os_index=1, logical_index=1)
                PU(os_index=1, logical_index=2)
                PU(os_index=5, logical_index=3)
            Core(os_index=2, logical_index=2)
                PU(os_index=2, logical_index=4)
                PU(os_index=6, logical_index=5)
            Core(os_index=3, logical_index=3)
                PU(os_index=3, logical_index=6)
                PU(os_index=7, logical_index=7)
        """
        hwloc_calc_values = [
            b'0',
            b'0,1,2,3',
            b'0,1,2,3,4,5,6,7'
        ]

        with unittest.mock.patch(
            target = 'subprocess.check_output',
            side_effect = hwloc_calc_values,
        ):
            st = SystemTopology(load = False)
            st._parse(filename = 'tests/data/intel-core-i7-4790.xml')

            subprocess.check_output.assert_has_calls([
                call(args=[
                    'hwloc-calc', '-I', 'Package', '--physical-input', '--logical-output',
                    'Package:0'
                ]),
                call(args=[
                    'hwloc-calc', '-I', 'Core',    '--physical-input', '--logical-output',
                    'Package:0.Core:0',
                    'Package:0.Core:1',
                    'Package:0.Core:2',
                    'Package:0.Core:3'
                ]),
                call(args=[
                    'hwloc-calc', '-I', 'PU',      '--physical-input', '--logical-output',
                    'Package:0.Core:0.PU:0', 'Package:0.Core:0.PU:4',
                    'Package:0.Core:1.PU:1', 'Package:0.Core:1.PU:5',
                    'Package:0.Core:2.PU:2', 'Package:0.Core:2.PU:6',
                    'Package:0.Core:3.PU:3', 'Package:0.Core:3.PU:7'
                ])
            ])

            # There is 1 package.
            assert len(st.packages) == 1

            # The package has 4 cores.
            assert len(st.packages[0].cores) == 4

            # Each core has 2 PUs.
            assert len(st.packages[0].cores[0].pus) == 2

            # The first PU of the second core of the package has OS index 1 and logical index 2.
            assert st.packages[0].cores[1].pus[0].os_index      == 1
            assert st.packages[0].cores[1].pus[0].logical_index == 2

            # The second PU of the second core of the package has OS index 5 and logical index 3.
            assert st.packages[0].cores[1].pus[1].os_index      == 5
            assert st.packages[0].cores[1].pus[1].logical_index == 3
