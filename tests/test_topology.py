import itertools
import subprocess
import unittest
from unittest.mock import call

from hwloc_xml_parser.topology import SystemTopology

class TestSystemTopology:
    """
        Test :py:class:`system.SystemTopology`.
    """

    def test_parse_single_intel_core_i7_4790(self):
        """
        The test reads an `xml` file with the output of `lstopo-no-graphics`
        for a single `Intel Core i7 4790` machine with the following topology:

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
            st._parse(filename = 'tests/data/single-intel-core-i7-4790.xml')

            subprocess.check_output.assert_has_calls([
                call(args=[
                    'hwloc-calc', '-I', 'Package', '--physical-input', '--logical-output',
                    'Package:0'
                ]),
                call(args=[
                    'hwloc-calc', '-I', 'Core', '--physical-input', '--logical-output',
                    'Package:0.Core:0',
                    'Package:0.Core:1',
                    'Package:0.Core:2',
                    'Package:0.Core:3'
                ]),
                call(args=[
                    'hwloc-calc', '-I', 'PU', '--physical-input', '--logical-output',
                    'Package:0.Core:0.PU:0', 'Package:0.Core:0.PU:4',
                    'Package:0.Core:1.PU:1', 'Package:0.Core:1.PU:5',
                    'Package:0.Core:2.PU:2', 'Package:0.Core:2.PU:6',
                    'Package:0.Core:3.PU:3', 'Package:0.Core:3.PU:7'
                ])
            ])

            # The machine has 1 package.
            assert len(st.packages) == 1
            assert st.get_num_packages() == 1

            # The package has 4 cores.
            package = st.packages[0]

            assert len(package.cores) == 4
            assert package.get_num_cores() == 4

            # The first core of the package has 2 PUs.
            assert len(package.cores[0].pus) == 2
            assert package.cores[0].get_num_pus() == 2

            # The first PU of the second core of the package has OS index 1 and logical index 2.
            assert package.cores[1].pus[0].os_index      == 1
            assert package.cores[1].pus[0].logical_index == 2

            # Repeat the last assertions, but using this time the generator returned by the
            # method :py:meth:`hwloc_xml_parser.topology.SystemTopology.recurse_cores`.
            core_1 = next(itertools.islice(st.recurse_cores(), 1, None))
            assert core_1.pus[0].os_index      == 1
            assert core_1.pus[0].logical_index == 2

            # Repeat the last assertions, but using this time the generator returned by the
            # method :py:meth:`hwloc_xml_parser.topology.SystemTopology.recurse_pus`.
            pu_2 = next(itertools.islice(st.recurse_pus(), 2, None))
            assert pu_2.os_index      == 1
            assert pu_2.logical_index == 2

            # The second PU of the second core of the package has OS index 5 and logical index 3.
            assert package.cores[1].pus[1].os_index      == 5
            assert package.cores[1].pus[1].logical_index == 3

            # All cores of the package have 2 PUs.
            assert package.all_equal_num_pus_per_core()

            # The machine has 4 cores in total.
            assert st.get_num_cores() == 4

            # The machine has 8 PUs in total.
            assert st.get_num_pus() == 8
            assert package.get_num_pus() == 8

            # All cores of the machine have the same number of PUs.
            assert st.all_equal_num_pus_per_core()

    def test_parse_dual_intel_xeon_gold_6126(self):
        """
        The test reads an `xml` file with the output of `lstopo-no-graphics`
        for a dual `Intel Xeon Gold 6126` machine with the following topology:

        .. code-block:: python

            Package(os_index=0, logical_index=0)
                Core(os_index=0, logical_index=0)
                    PU(os_index=0,  logical_index=0)
                    PU(os_index=24, logical_index=1)
                Core(os_index=1, logical_index=1)
                    PU(os_index=1,  logical_index=2)
                    PU(os_index=25, logical_index=3)
                ...
                Core(os_index=6, logical_index=6)
                    PU(os_index=6,  logical_index=12)
                    PU(os_index=30, logical_index=13)
                Core(os_index=8, logical_index=7)
                    PU(os_index=7,  logical_index=14)
                    PU(os_index=31, logical_index=15)
                Core(os_index=10, logical_index=8)
                    PU(os_index=8,  logical_index=16)
                    PU(os_index=32, logical_index=17)
                ...
                Core(os_index=13, logical_index=11)
                    PU(os_index=11, logical_index=22)
                    PU(os_index=35, logical_index=23)
            Package(os_index=1, logical_index=1)
                Core(os_index=1, logical_index=12)
                    PU(os_index=12, logical_index=24)
                    PU(os_index=36, logical_index=25)
                ...
                Core(os_index=6, logical_index=17)
                    PU(os_index=17, logical_index=34)
                    PU(os_index=41, logical_index=35)
                Core(os_index=8, logical_index=18)
                    PU(os_index=18, logical_index=36)
                    PU(os_index=42, logical_index=37)
                ...
                Core(os_index=13, logical_index=23)
                    PU(os_index=23, logical_index=46)
                    PU(os_index=47, logical_index=47)
        """
        hwloc_calc_values = [
            b'0,1',
            ','.join([str(i) for i in range(24)]).encode(),
            ','.join([str(i) for i in range(48)]).encode()
        ]

        with unittest.mock.patch(
            target = 'subprocess.check_output',
            side_effect = hwloc_calc_values,
        ):
            st = SystemTopology(load = False)
            st._parse(filename = 'tests/data/dual-intel-xeon-gold-6126.xml')

            subprocess.check_output.assert_has_calls([
                call(args=[
                    'hwloc-calc', '-I', 'Package', '--physical-input', '--logical-output',
                    'Package:0',
                    'Package:1'
                ]),
                call(args=[
                    'hwloc-calc', '-I', 'Core', '--physical-input', '--logical-output',
                    'Package:0.Core:0',
                    'Package:0.Core:1',
                    'Package:0.Core:2',
                    'Package:0.Core:3',
                    'Package:0.Core:4',
                    'Package:0.Core:5',
                    'Package:0.Core:6',
                    'Package:0.Core:8',
                    'Package:0.Core:10',
                    'Package:0.Core:11',
                    'Package:0.Core:12',
                    'Package:0.Core:13',
                    'Package:1.Core:1',
                    'Package:1.Core:2',
                    'Package:1.Core:3',
                    'Package:1.Core:4',
                    'Package:1.Core:5',
                    'Package:1.Core:6',
                    'Package:1.Core:8',
                    'Package:1.Core:9',
                    'Package:1.Core:10',
                    'Package:1.Core:11',
                    'Package:1.Core:12',
                    'Package:1.Core:13'
                ]),
                call(args=[
                    'hwloc-calc', '-I', 'PU', '--physical-input', '--logical-output',
                    'Package:0.Core:0.PU:0',   'Package:0.Core:0.PU:24',
                    'Package:0.Core:1.PU:1',   'Package:0.Core:1.PU:25',
                    'Package:0.Core:2.PU:2',   'Package:0.Core:2.PU:26',
                    'Package:0.Core:3.PU:3',   'Package:0.Core:3.PU:27',
                    'Package:0.Core:4.PU:4',   'Package:0.Core:4.PU:28',
                    'Package:0.Core:5.PU:5',   'Package:0.Core:5.PU:29',
                    'Package:0.Core:6.PU:6',   'Package:0.Core:6.PU:30',
                    'Package:0.Core:8.PU:7',   'Package:0.Core:8.PU:31',
                    'Package:0.Core:10.PU:8',  'Package:0.Core:10.PU:32',
                    'Package:0.Core:11.PU:9',  'Package:0.Core:11.PU:33',
                    'Package:0.Core:12.PU:10', 'Package:0.Core:12.PU:34',
                    'Package:0.Core:13.PU:11', 'Package:0.Core:13.PU:35',
                    'Package:1.Core:1.PU:12',  'Package:1.Core:1.PU:36',
                    'Package:1.Core:2.PU:13',  'Package:1.Core:2.PU:37',
                    'Package:1.Core:3.PU:14',  'Package:1.Core:3.PU:38',
                    'Package:1.Core:4.PU:15',  'Package:1.Core:4.PU:39',
                    'Package:1.Core:5.PU:16',  'Package:1.Core:5.PU:40',
                    'Package:1.Core:6.PU:17',  'Package:1.Core:6.PU:41',
                    'Package:1.Core:8.PU:18',  'Package:1.Core:8.PU:42',
                    'Package:1.Core:9.PU:19',  'Package:1.Core:9.PU:43',
                    'Package:1.Core:10.PU:20', 'Package:1.Core:10.PU:44',
                    'Package:1.Core:11.PU:21', 'Package:1.Core:11.PU:45',
                    'Package:1.Core:12.PU:22', 'Package:1.Core:12.PU:46',
                    'Package:1.Core:13.PU:23', 'Package:1.Core:13.PU:47'
                ])
            ])

            # There are 2 packages.
            assert len(st.packages) == 2
            assert st.get_num_packages() == 2

            # The first package has 12 cores.
            first_package = st.packages[0]

            assert len(first_package.cores) == 12
            assert first_package.get_num_cores() == 12

            # The first core of the first package has 2 PUs.
            assert len(first_package.cores[0].pus) == 2
            assert first_package.cores[0].get_num_pus() == 2

            # All cores of the first package have 2 PUs.
            assert first_package.all_equal_num_pus_per_core()

            # The machine has 24 cores in total.
            assert st.get_num_cores() == 24

            # The machine has 48 PUs in total.
            assert st.get_num_pus() == 48

            # All cores of the machine have the same number of PUs.
            assert st.all_equal_num_pus_per_core()

    def test_parse_single_nvidia_jetson_xavier_agx(self):
        """
        The test reads an `xml` file with the output of `lstopo-no-graphics`
        for a single `Nvidia Jetson Xavier AGX` machine.
        """
        hwloc_calc_values = [
            b'0,1,2,3',
            b'0,1,2,3,4,5,6,7',
            b'0,1,2,3,4,5,6,7'
        ]

        with unittest.mock.patch(
            target = 'subprocess.check_output',
            side_effect = hwloc_calc_values,
        ):
            st = SystemTopology(load = False)
            st._parse(filename = 'tests/data/single-nvidia-jetson-xavier-agx.xml')

            # There are 4 packages.
            # This is how `hwloc` reports it. Physically, there is a single package, with 4 clusters of 2 cores each.
            #
            # See also:
            #     - https://www.anandtech.com/show/13584/nvidia-xavier-agx-hands-on-carmel-and-more
            assert st.get_num_packages() == 4

            # The machine has 8 cores in total.
            assert st.get_num_cores() == 8

            # The machine has 8 PUs in total.
            assert st.get_num_pus() == 8

            # All cores of the machine have the same number of PUs.
            assert st.all_equal_num_pus_per_core()

    def test_parse_single_apple_m2(self):
        """
        The test reads an `xml` file with the output of `lstopo-no-graphics`
        for a single `Apple M2` machine.
        """
        hwloc_calc_values = [
            b'0',
            b'0,1,2,3,4,5,6,7',
            b'0,1,2,3,4,5,6,7'
        ]

        with unittest.mock.patch(
            target = 'subprocess.check_output',
            side_effect = hwloc_calc_values,
        ):
            st = SystemTopology(load = False)
            st._parse(filename = 'tests/data/single-apple-m2.xml')

            # The machine has 1 package.
            assert st.get_num_packages() == 1

            # The machine has 8 cores in total.
            assert st.get_num_cores() == 8

            # The machine has 8 PUs in total.
            assert st.get_num_pus() == 8

            # All cores of the machine have the same number of PUs.
            assert st.all_equal_num_pus_per_core()

    def test_parse(self):
        """
        Run the tool and check that it parses to something meaningful, whatever the machine.
        """
        st = SystemTopology(load = True)

        assert st.get_num_pus() > 0
