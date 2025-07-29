import unittest
import funcnodes_numpy as fnp

import funcnodes as fn


def get_module_nodes(module):
    nodes = [getattr(module, node) for node in dir(module)]
    nodes = [
        node for node in nodes if isinstance(node, type) and issubclass(node, fn.Node)
    ]
    return nodes


class TestGeneral(unittest.IsolatedAsyncioTestCase):
    def test_main_shelf(self):
        shelf = fnp.NODE_SHELF
        self.assertEqual(shelf.name, "numpy")
        self.assertEqual(len(shelf.nodes), 0)
        self.assertEqual(len(shelf.subshelves), 16)

    def test_all_nodes(self):
        nodes = get_module_nodes(fnp)
        exp = 307
        exp_shelfnodes = 374
        if fnp.np_version["major_int"] < 2:
            exp -= 1
            exp_shelfnodes -= 1
        if fnp.np_version["major_int"] >= 2 and fnp.np_version["minor_int"] >= 2:
            exp += 3
            exp_shelfnodes += 3
        self.assertEqual(len(nodes) + 1, exp)
        for node in nodes:
            print(node.node_name)

        shelvenodes, _ = fn.flatten_shelf(fnp.NODE_SHELF)
        missing_shelvenodes = set(nodes) - (set(shelvenodes))
        self.assertEqual(
            len(missing_shelvenodes), 1, [n.node_name for n in missing_shelvenodes]
        )

        self.assertEqual(len(shelvenodes), exp_shelfnodes)

    async def test_ndarray_shelve(self):
        shelf = fnp._ndarray.NODE_SHELF
        shelve_nodes, _ = fn.flatten_shelf(shelf)
        module_nodes = get_module_nodes(fnp._ndarray)
        self.assertEqual(len(shelve_nodes), len(module_nodes))
        self.assertEqual(len(shelve_nodes), 49)

    async def test_linalg_shelve(self):
        shelf = fnp._linalg.NODE_SHELF
        shelve_nodes, _ = fn.flatten_shelf(shelf)
        module_nodes = get_module_nodes(fnp._linalg)
        self.assertEqual(len(shelve_nodes), len(module_nodes))
        self.assertEqual(len(shelve_nodes), 20)

    async def test_emath_shelve(self):
        shelf = fnp._lib.EMATH_NODE_SHELF
        shelve_nodes, _ = fn.flatten_shelf(shelf)
        module_nodes = get_module_nodes(fnp._lib.scimath)
        self.assertEqual(len(shelve_nodes), len(module_nodes))
        self.assertEqual(len(shelve_nodes), 9)

    async def test_core_shelve(self):
        exp_nodes = 261
        if fnp.np_version["major_int"] < 2:
            exp_nodes -= 1
        if fnp.np_version["major_int"] >= 2 and fnp.np_version["minor_int"] >= 2:
            exp_nodes += 3
        module_nodes = get_module_nodes(fnp._core)
        self.assertEqual(len(module_nodes), exp_nodes)
