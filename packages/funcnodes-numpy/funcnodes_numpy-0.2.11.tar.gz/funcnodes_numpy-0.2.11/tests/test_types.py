import unittest
import funcnodes_numpy as fnp
from typing import Union, List, Literal, TYPE_CHECKING
import numpy as np
import json
import funcnodes as fn
from exposedfunctionality.function_parser.types import (
    string_to_type,
    _TYPE_GETTER,
    type_to_string,
)


def flatten_shelves(shelf: fn.Shelf) -> list[fn.Node]:
    nodes = shelf["nodes"]
    subshelves = shelf["subshelves"]
    for subshelf in subshelves:
        nodes.extend(flatten_shelves(subshelf))
    return set(nodes)


class TestTypes(unittest.TestCase):
    def test_typestrings(self):
        shelf = fnp.NODE_SHELF
        nodes, _ = fn.flatten_shelf(shelf)

        def _test_typestring(t):
            if isinstance(t, str):
                self.assertEqual(type_to_string(string_to_type(t)), t)
            elif isinstance(t, dict):
                if "anyOf" in t:
                    for _t in t["anyOf"]:
                        _test_typestring(_t)
                elif "allOf" in t:
                    for _t in t["allOf"]:
                        _test_typestring(_t)
                elif "type" in t:
                    if t["type"] == "array":
                        _test_typestring(t["items"])
                    elif t["type"] == "enum":
                        return
                    else:
                        raise ValueError(f"{t}, ({type(t)})")
                else:
                    raise ValueError(f"{t}, ({type(t)})")
            else:
                raise ValueError(f"{t}, ({type(t)})")

        for node in nodes:
            ins: fn.Node = node()
            for ipname, ip in ins.inputs.items():
                t = json.loads(
                    json.dumps(ip.serialize_class()["type"], cls=fn.JSONEncoder)
                )
                try:
                    _test_typestring(t)

                except Exception as e:
                    raise ValueError(
                        f"failed typestring test for {node.node_name} input: {ipname}, {t}"
                    ) from e
            for ipname, ip in ins.outputs.items():
                t = ip.serialize_class()["type"]
                try:
                    _test_typestring(t)
                except Exception as e:
                    print(_TYPE_GETTER)
                    raise ValueError(
                        f"failed typestring test for {node.node_name} output: {ipname}"
                    ) from e

    def test_types_to_string(self):
        for i, (src, exp, exps) in enumerate(
            [
                (
                    fnp.DTYPE_ENUM,
                    fnp.DTYPE_ENUM,
                    "funcnodes_numpy._dtypes.DTYPE_ENUM",
                ),  # 0
                (fnp._types.scalar, Union[float, int], "Union[float, int]"),  # 1
                (
                    fnp._types.number,
                    Union[complex, float, int],
                    "Union[complex, float, int]",
                ),  # 2
                (
                    fnp._types.ndarray_or_scalar,
                    Union[
                        fnp._types.scalar,
                        np.ndarray,
                    ],
                    "Union[float, int, ndarray]",
                ),  # 3
                (
                    fnp._types.ndarray_or_number,
                    Union[fnp._types.number, np.ndarray],
                    "Union[complex, float, int, ndarray]",
                ),  # 4
                (
                    fnp._types.indices_or_sections,
                    Union[int, List[int]],
                    "Union[int, List[int]]",
                ),  # 5
                (
                    fnp._types.shape_like,
                    Union[np.ndarray, int, List[int]],
                    "Union[ndarray, int, List[int]]",
                ),  # 6
                (
                    fnp._types.axis_like,
                    Union[int, List[int]],
                    "Union[int, List[int]]",
                ),  # 7
                (fnp._types.ndarray, np.ndarray, "ndarray"),  # 8
                (
                    fnp._types.array_like,
                    Union[float, int, complex, str, bool, np.ndarray],
                    "Union[float, int, complex, str, bool, ndarray]",
                ),  # 9
                (fnp._types.int_array, np.ndarray, "ndarray"),  # 10
                (fnp._types.bool_array, np.ndarray, "ndarray"),  # 11
                (fnp._types.bitarray, np.ndarray, "ndarray"),  # 12
                (
                    fnp._types.bool_or_bool_array,
                    Union[bool, fnp._types.bool_array],
                    "Union[bool, ndarray]",
                ),  # 13
                (
                    fnp._types.int_bool_array,
                    Union[fnp._types.int_array, fnp._types.bool_array],
                    "ndarray",
                ),  # 14
                (
                    fnp._types.int_or_int_array,
                    Union[int, fnp._types.int_array],
                    "Union[int, ndarray]",
                ),  # 15
                (fnp._types.real_array, np.ndarray, "ndarray"),  # 16
                (fnp._types.matrix, np.ndarray, "ndarray"),  # 17
                (
                    fnp._types.OrderCF,
                    Literal[None, "C", "F"],
                    "Literal[None, 'C', 'F']",
                ),  # 18
                (
                    fnp._types.OrderKACF,
                    Literal[None, "K", "A", "C", "F"],
                    "Literal[None, 'K', 'A', 'C', 'F']",
                ),  # 19
                (
                    fnp._types.OrderACF,
                    Literal[None, "A", "C", "F"],
                    "Literal[None, 'A', 'C', 'F']",
                ),  # 20
                (
                    fnp._types.buffer_like,
                    Union[bytes, bytearray, memoryview, np.ndarray],
                    "Union[bytes, bytearray, memoryview, ndarray]",
                ),  # 21
                (
                    fnp._types.str_array,
                    np._ArrayLikeStr_co
                    if TYPE_CHECKING
                    else np._typing._ArrayLikeStr_co,
                    "Union[numpy._typing._array_like._SupportsArray, numpy._typing._nested_sequence._NestedSequence, "
                    "str, numpy._typing._nested_sequence._NestedSequence]",
                ),  # 22
                (fnp._types.NoValue, np._NoValue, "<no value>"),  # 23
                (
                    fnp._types.casting_literal,
                    Literal["no", "equiv", "safe", "same_kind", "unsafe"],
                    "Literal['no', 'equiv', 'safe', 'same_kind', 'unsafe']",
                ),  # 24
            ]
        ):
            self.assertEqual(type_to_string(src), type_to_string(exp), (i, src, exp))
            self.assertEqual(type_to_string(src), exps, (i, src, exps))

    def test_enum_options(self):
        node = fnp.astype()

        self.assertEqual(
            node.get_input("dtype").value_options["options"]["keys"],
            [i.name for i in fnp.DTYPE_ENUM],
        )
        self.assertEqual(
            node.get_input("dtype").value_options["options"]["values"],
            [i.value for i in fnp.DTYPE_ENUM],
        )

    def test_literal_options(self):
        node = fnp.newbyteorder()
        self.assertEqual(
            node.get_input("new_order").value_options["options"]["values"],
            ["S", "<", ">", "=", "|"],
        )
