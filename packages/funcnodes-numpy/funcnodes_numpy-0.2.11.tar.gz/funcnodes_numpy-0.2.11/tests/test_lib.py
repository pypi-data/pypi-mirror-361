import unittest
import funcnodes_numpy as fnp
import funcnodes as fn
import numpy as np
import inspect
from exposedfunctionality import controlled_unwrap as unwrap
import os

from exposedfunctionality import controlled_wrapper as wraps


@wraps(np.e, wrapper_attribute="__fnwrapped__")
def _testf():
    return 1


class TestNumpyLib(unittest.TestCase):
    def test_ufunc_completness(self):
        nodes, _ = fn.flatten_shelf(fnp.NODE_SHELF)
        node_names = sorted([node.node_name for node in nodes])
        all_funcs = fnp.ufuncs.get_numpy_ufucs()
        print(all_funcs)
        self.assertIn("add", all_funcs)
        self.assertIn("subtract", all_funcs)
        self.assertIn("sin", all_funcs)
        self.assertIn("cos", all_funcs)
        self.assertIn("sqrt", all_funcs)
        self.assertIn("exp", all_funcs)

        for f in all_funcs:
            self.assertIn(f, node_names)

        for f in all_funcs:
            for node in nodes:
                if node.node_name == f:
                    srcf = inspect.getsourcefile(unwrap(node.func))
                    bdir = os.path.dirname(os.path.dirname(inspect.getsourcefile(fn)))
                    memdata = "\n  ".join(
                        [
                            str(
                                (
                                    inspect.getsourcefile(v).replace(bdir, ""),
                                    hasattr(v, "__wrapped__"),
                                )
                            )
                            for v in unwrap(node.func, return_memo=True)[1].values()
                        ]
                    )
                    self.assertTrue(
                        srcf.endswith("ufuncs.py")
                        or srcf.endswith("scimath.py")
                        or srcf.endswith("_ndarray.py"),
                        f"souce file for {f} is {srcf} not ufuncs.py, [\n  {memdata}\n]",
                    )

    def test_calls(self):
        import inspect

        print(inspect.getsource(_testf))
