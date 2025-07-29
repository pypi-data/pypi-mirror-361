from all_nodes_test_base import TestAllNodesBase
import numpy as np
import funcnodes_numpy as fnp
import funcnodes as fn
import unittest


samplemap = {
    "ndarray": lambda: [
        np.array([1, 2, 3]),
        np.array([0, 1]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
        np.arange(2 * 2 * 2).reshape(2, 2, 2),
        np.array([1, 2, 3], dtype=np.float32),
        np.array([[2], [7], [23]], dtype=np.uint8),
        np.array([1 + 2j, 3 + 4j]),
    ],
    "Union[bool, complex, float, int, ndarray, str]": lambda: [
        True,
        1j,
        1.0,
        1,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
        np.arange(2 * 2 * 2).reshape(2, 2, 2),
        np.datetime64("2021-01-01"),
        "str",
    ],
    "Union[None, float]": lambda: [None, 1.0],
    "Union[None, float, int]": lambda: [None, 1.0, 1],
    "Union[None, int]": lambda: [None, 1],
    "Union[None, bool]": lambda: [None, True],
    "Union[None, ndarray]": lambda: [
        None,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    "Union[None, dict]": lambda: [None, {"a": lambda: 1}],
    "Union[None, Sequence[Tuple[float, float]]]": lambda: [None, [(1.0, 2.0)]],
    "Union[None, Sequence[int]]": lambda: [None, [1, 2, 3]],
    "Union[None, Sequence[Union[float, int]]]": lambda: [None, [1, 2, 3]],
    "Union[List[int], int]": lambda: [[1, 2, 3], 1],
    "Union[List[int], None, int]": lambda: [[1, 2, 3], None, 1],
    "Union[Literal[1, 2], None]": lambda: [1, 2, None],
    "Union[None, float, int, ndarray]": lambda: [
        None,
        1.0,
        1,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    "Union[complex, float, int, ndarray]": lambda: [
        1j,
        1.0,
        1,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    (
        "Union[numpy._typing._array_like._SupportsArray, numpy._typing._nested_sequence._NestedSequence, "
        "numpy._typing._nested_sequence._NestedSequence, str]"
    ): lambda: [
        np.array([1, 2, 3]),
        [[1, 2, 3]],
        [[[1, 2, 3]]],
        "str",
    ],
    "Union[int, ndarray]": lambda: [
        0,
        1,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    "Union[Sequence[int], int]": lambda: [[1, 2, 3], 1],
    "Union[Sequence[Union[float, int]], Sequence[str], int]": lambda: [
        [1, 2, 3],
        ["a", "b", "c"],
        1,
    ],
    "Union[bytearray, bytes, memoryview, ndarray]": lambda: [
        bytearray(b"hello"),
        np.array([1, 2, 3]).tobytes(),
        memoryview(b"hello"),
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    "Union[float, int, ndarray]": lambda: [
        1.0,
        1,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    "Union[int, ndarray, str]": lambda: [
        1,
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
        "str",
    ],
    "Union[Literal['big', 'little'], None]": lambda: ["big", "little", None],
    "Union[None, int, ndarray]": lambda: [
        None,
        1,
        np.array([1, 2, 3, 4]).reshape(2, 2),
        np.array([1, 2, 3]),
    ],
    "Union[Literal['full', 'valid', 'same'], None]": lambda: [
        "full",
        "valid",
        "same",
        None,
    ],
    "Union[None, Tuple[float, float]]": lambda: [None, (1.0, 2.0)],
    "Union[None, bool, complex, float, int, ndarray, str]": lambda: [
        None,
        True,
        1j,
        1.0,
        1,
        np.array([1, 2, 3, 4]).reshape(2, 2),
        np.array([1, 2, 3]),
        "str",
    ],
    "Union[None, funcnodes_numpy._dtypes.DTYPE_ENUM]": lambda: [None, "f", bool],
    "Union[List[int], None]": lambda: [[1, 2, 3], None],
    "Union[Tuple[Union[int, ndarray], Union[int, ndarray]], int, ndarray]": lambda: [
        (1, np.array([1, 2, 3])),
        np.array([1, 2, 3, 4]).reshape(2, 2),
        np.array([1, 2, 3]),
        1,
    ],
    "Union[Tuple[Union[float, int], Union[float, int]], float, int]": lambda: [
        (1.0, 2.0),
        1.0,
        1,
    ],
    "Literal['reduced', 'complete', 'r', 'raw']": lambda: [
        "reduced",
        "complete",
        "r",
        "raw",
    ],
    "int": lambda: [1, 2, 0],
    "List[ndarray]": lambda: [
        [
            np.array([3, 2, 1]),
            np.array([1, 2, 3]),
        ],
        np.arange(25).reshape(1, 5, 5),
    ],
    "typing.Callable": lambda: [lambda x: x],
    "funcnodes_numpy._dtypes.DTYPE_ENUM": lambda: ["f", bool],
    "float": lambda: [1.0, 1],
    "List[Union[float, int, ndarray]]": lambda: [
        [1.0, 1, np.array([1, 2, 3, 4]).reshape(2, 2), np.array([1, 2, 3])]
    ],
    "Union[Literal['fro', 'nuc'], None, float]": lambda: ["fro", "nuc", None, 1.0],
    "List[Union[bool, complex, float, int, ndarray, str]]": lambda: [
        [
            True,
            1j,
            1.0,
            1,
            np.array([1, 2, 3, 4]).reshape(2, 2),
            np.array([1, 2, 3]),
            "str",
        ]
    ],
    "Union[float, int]": lambda: [1.0, 1],
    "bool": lambda: [True, False],
    "Union[None, str]": lambda: [None, "str"],
    "Literal['left', 'right']": lambda: ["left", "right"],
    "Union[ndarray, str]": lambda: [np.array([1, 2, 3]), "str"],
    "Sequence[ndarray]": lambda: [
        [np.array([1, 2, 3, 4]).reshape(2, 2), np.array([1, 2, 3])],
        [np.array([4, 3, 2]), np.array([1, 2, 3])],
    ],
    "Literal['L', 'U']": lambda: ["L", "U"],
    "builtins.object": lambda: [object(), np.array([1, 2, 3])],
    "Literal['raise', 'wrap', 'clip']": lambda: ["raise", "wrap", "clip"],
    "Sequence[Union[bool, complex, float, int, ndarray, str]]": lambda: [
        [True, 1j, 1.0, 1, np.array([1, 2, 3]), "str"]
    ],
    "Union[List[Tuple[int, int]], Tuple[int, int], int]": lambda: [
        [(1, 2), (3, 4)],
        (1, 2),
        1,
    ],
    "Union[Literal[False, True, 'greedy', 'optimal'], None]": lambda: [
        False,
        True,
        "greedy",
        "optimal",
        None,
    ],
    "List[Union[float, int]]": lambda: [[1.0, 1], [2.0, 1]],
    "Literal['xy', 'ij']": lambda: ["xy", "ij"],
    "Literal['F', 'C', 'A', 'W', 'O', 'E']": lambda: ["F", "C", "A", "W", "O", "E"],
    "Sequence[float]": lambda: [[1.0, 2.0, 3.0]],
    "Any": lambda: [1, 1.0, "str", True],
    "Literal['S', '<', '>', '=', '|']": lambda: ["S", "<", ">", "=", "|"],
    "typing.Iterable": lambda: [[1, 2, 3]],
    (
        "Literal['constant', 'edge', 'linear_ramp', 'maximum', 'mean', 'median', 'minimum', "
        "'reflect', 'symmetric', 'wrap', 'empty']"
    ): lambda: [
        "constant",
        "edge",
        "linear_ramp",
        "maximum",
        "mean",
        "median",
        "minimum",
        "reflect",
        "symmetric",
        "wrap",
        "empty",
    ],
    "str": lambda: ["str", "ii", "ij,jk,kl->il", "2005-02-25"],
    "Union[int, List[int], None]": lambda: [1, [1, 2, 3], None],
    "Union[ndarray, int, List[int]]": lambda: [
        np.array([1, 2, 3]),
        1,
        [1, 2, 3],
        [-1, 1],
    ],
    "Union[str, int, ndarray]": lambda: ["str", 1, np.array([1, 2, 3]), "2005-02-25"],
    "Union[float, int, Tuple[Union[float, int], Union[float, int]]]": lambda: [
        1,
        1.0,
        (1, 2),
    ],
    "Union[List[Union[float, int, ndarray]], None]": lambda: [
        [1, 1.0, np.array([1, 2, 3])],
        None,
    ],
    "Union[float, int, complex, str, bool, ndarray]": lambda: [
        1,
        1.0,
        1j,
        "str",
        True,
        np.array([1, 2, 3]),
        np.arange(2 * 2 * 2).reshape(2, 2, 2),
        np.array([[1, -2j], [2j, 5]]),
        np.eye(4 * 6).reshape(4, 6, 8, 3),
        np.datetime64("NaT"),
        np.nan,
    ],
    "Union[float, int, complex, str, bool, ndarray, None]": lambda: [
        1,
        1.0,
        1j,
        "str",
        True,
        np.array([1, 2, 3]),
        None,
    ],
    "Union[int, Tuple[int, int], List[Tuple[int, int]]]": lambda: [
        1,
        (1, 2),
        [(1, 2), (3, 4)],
    ],
    "Sequence[Union[float, int, complex, str, bool, ndarray]]": lambda: [
        [1, 1.0, 1j, "str", True, np.array([1, 2, 3])],
        np.arange(2 * 2 * 2).reshape(2, 2, 2).tolist(),
    ],
    "Union[int, ndarray, Tuple[Union[int, ndarray], Union[int, ndarray]]]": lambda: [
        1,
        np.array([1, 2, 3]),
        (1, np.array([1, 2, 3])),
        (1, 0),
    ],
    "List[Union[float, int, complex, str, bool, ndarray]]": lambda: [
        [
            1,
            1.0,
            1j,
            "str",
            True,
            np.array([1, 2, 3]),
        ],
        [np.arange(2), np.arange(3)],
        [np.random.rand(2, 2), np.random.rand(2, 5), np.random.rand(5, 2)],
    ],
    "Union[bytes, bytearray, memoryview, ndarray]": lambda: [
        b"12345678",
        np.array([1, 2, 3]).tobytes(),
        bytearray(b"hello"),
        memoryview(b"hello"),
        np.array([1, 2, 3]),
        np.array([1, 2, 3, 4]).reshape(2, 2),
    ],
    (
        "Union[numpy._typing._array_like._SupportsArray, numpy._typing._nested_sequence._NestedSequence, "
        "str, numpy._typing._nested_sequence._NestedSequence]"
    ): lambda: [
        np.array([1, 2, 3]),
        [[1, 2, 3]],
        [[[1, 2, 3]]],
        "str",
    ],
    "bytes": lambda: [
        b"\x93NUMPY\x01\x00v\x00{'descr': '<i8', 'fortran_order': False, 'shape': (1,), }"
        b"                                                            \n\x01\x00\x00\x00\x00\x00\x00\x00",
    ],
}

samplemap["Union[float, int]"] = samplemap["Union[float, int]"]
samplemap["Union[float, None]"] = samplemap["Union[None, float]"]
samplemap["Union[ndarray, None]"] = samplemap["Union[None, ndarray]"]
samplemap["Union[dict, None]"] = samplemap["Union[None, dict]"]
samplemap["Union[int, None]"] = samplemap["Union[None, int]"]
samplemap["Union[bool, None]"] = samplemap["Union[None, bool]"]
samplemap["Union[str, None]"] = samplemap["Union[None, str]"]
samplemap["Union[float, int, None]"] = samplemap["Union[None, float, int]"]
samplemap["Union[Tuple[float, float], None]"] = samplemap[
    "Union[None, Tuple[float, float]]"
]
samplemap["Union[Sequence[Tuple[float, float]], None]"] = samplemap[
    "Union[None, Sequence[Tuple[float, float]]]"
]
samplemap["Union[Sequence[int], None]"] = samplemap["Union[None, Sequence[int]]"]
samplemap["Union[Sequence[Union[float, int]], None]"] = samplemap[
    "Union[None, Sequence[Union[float, int]]]"
]


samplemap["Union[float, int, None]"] = samplemap["Union[None, float, int]"]
samplemap["Union[funcnodes_numpy._dtypes.DTYPE_ENUM, None]"] = samplemap[
    "Union[None, funcnodes_numpy._dtypes.DTYPE_ENUM]"
]
samplemap["Union[int, Sequence[int]]"] = samplemap["Union[Sequence[int], int]"]
samplemap["Union[float, int, ndarray, None]"] = samplemap[
    "Union[None, float, int, ndarray]"
]
samplemap["List[Union[float, int]]"] = samplemap["List[Union[float, int]]"]
samplemap["Union[int, List[int]]"] = samplemap["Union[List[int], int]"]
samplemap["Union[int, Sequence[Union[float, int]], Sequence[str]]"] = samplemap[
    "Union[Sequence[Union[float, int]], Sequence[str], int]"
]
samplemap["Union[str, ndarray]"] = samplemap["Union[ndarray, str]"]
samplemap["Union[float, Literal['fro', 'nuc'], None]"] = samplemap[
    "Union[Literal['fro', 'nuc'], None, float]"
]
samplemap["Union[float, int, None]"] = samplemap["Union[None, float, int]"]


class TestLocalTypes(unittest.IsolatedAsyncioTestCase):
    async def test_missing_types(self):
        shelvenodes, _ = fn.flatten_shelf(fnp.NODE_SHELF)
        missing_types = set()
        missing_nodes = set()
        for node in shelvenodes:
            exf = node.func.ef_funcmeta
            for ip in exf["input_params"]:
                if ip["type"] not in samplemap:
                    missing_nodes.add(node.node_name)
                    missing_types.add(ip["type"])
                    continue

        self.assertEqual(len(missing_types), 0, f"{missing_types} from {missing_nodes}")
        for node in shelvenodes:
            exf = node.func.ef_funcmeta
            for ip in exf["input_params"]:
                assert isinstance(samplemap[ip["type"]](), list), (
                    f"{ip['type']} not a list"
                )


class TestAllNodes(TestAllNodesBase):
    # in this test class all nodes should be triggered at least once to mark them as testing
    async def test_nodes(self):
        # shelvenodes = flatten_shelves(fnp.NODE_SHELF)
        skip = [fnp.clip]
        for node in self.all_nodes:
            if node in skip:
                continue
            ins = node()
            exf = node.func.ef_funcmeta

            kwargs = {}
            args = []
            types = []
            for ip in exf["input_params"]:
                if ip["positional"]:
                    newargs = []
                    types.append(ip["type"])
                    try:
                        options = samplemap[ip["type"]]()
                    except KeyError as e:
                        raise KeyError(
                            f"KeyError for {node.node_name}{ip['type']}"
                        ) from e
                    for option in options:
                        if len(args) == 0:
                            newargs.append([option])
                        else:
                            for a in args:
                                newargs.append(a + [option])
                    args = newargs
                else:
                    kwargs[ip["name"]] = samplemap[ip["type"]]()[0]

            errors = []
            if len(args) == 0:
                args = [()]
                # raise ValueError(f"len args 0 for  {node.node_name} ")
            run = False
            for a in args:
                try:
                    _ = await ins.func(
                        *a,
                    )
                    run = True
                    self.nodes_to_test.remove(node)
                    break
                except Exception as e:
                    errors.append((str(e), a))
            if not run:
                print(types)
                errors = "\n".join([f"{e[0]} with {e[1]}" for e in errors])
                raise Exception(
                    f"Failed to run {node.node_name} with types {types}:\n {errors} \n {run}"
                )

    async def test_clip(self):
        node = fnp.clip()
        node.inputs["a"].value = np.array([0, 1, 2, 3])
        node.inputs["a_min"].value = 1
        await node

        self.assertTrue(np.all(node.outputs["out"].value == np.array([1, 1, 2, 3])))

    async def test_node_format(self):
        for node in self.all_nodes:
            ins = node()
            self.assertGreater(len(ins.outputs), 0, f"{node.node_name} has no outputs")
            self.assertGreater(len(ins.inputs), 0, f"{node.node_name} has no inputs")
