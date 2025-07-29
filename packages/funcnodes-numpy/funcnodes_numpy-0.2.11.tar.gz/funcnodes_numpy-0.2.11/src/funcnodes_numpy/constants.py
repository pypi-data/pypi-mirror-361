import funcnodes as fn


from ._core.ufuncs import euler_gamma, pi, e

NODE_SHELF = fn.Shelf(
    name="constants",
    description="constants",
    nodes=[e, euler_gamma, pi],
    subshelves=[],
)
