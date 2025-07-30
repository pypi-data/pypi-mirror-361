"""
Utility modules required for JAX implementation.

# Copyright(C) 2022 Gordian Edenhofer
# SPDX-License-Identifier: GPL-2.0+ OR BSD-2-Clause
# Authors: Gordian Edenhofer, Philipp Frank
"""

import operator
from abc import ABCMeta
from dataclasses import dataclass
from functools import partial
from typing_extensions import Union

import jax
from jax.tree_util import register_pytree_node, register_pytree_node_class, tree_map

"""
Below code is used to define the metaclass that is used for all subsequent definitions
of classes used in this module. It properly takes care of extending PyTree definitions
to 

Obtained from ift/NIFTy/src/re/model.py

# SPDX-License-Identifier: GPL-2.0+ OR BSD-2-Clause 
"""


class ModelMeta(ABCMeta):
    """Register all derived classes as PyTrees in JAX using metaprogramming.

    For any dataclasses.Field property with a metadata-entry named "static",
    we will either hide or expose the property to JAX depending on the value.
    """

    def __new__(mcs, name, bases, dict_, /, **kwargs):
        cls = super().__new__(mcs, name, bases, dict_, **kwargs)
        cls = dataclass(init=False, repr=False, eq=False)(cls)
        IS_STATIC_DEFAULT = True

        def tree_flatten(self):
            static = []
            dynamic = []
            for k, v in self.__dict__.items():
                # Inspired by how equinox registers properties as static in JAX
                fm = self.__dataclass_fields__.get(k)
                fm = fm.metadata if fm is not None else {}
                if fm.get("static", IS_STATIC_DEFAULT) is False:
                    dynamic.append((PyTreeString(k), v))
                else:
                    static.append((k, v))
            return (tuple(dynamic), tuple(static))

        @partial(partial, cls=cls)
        def tree_unflatten(aux, children, *, cls):
            static, dynamic = aux, children
            obj = object.__new__(cls)
            for nm, m in dynamic + static:
                setattr(obj, str(nm), m)  # unwrap any potential `PyTreeSring`s
            return obj

        # Register class and all classes deriving from it
        register_pytree_node(cls, tree_flatten, tree_unflatten)
        return cls


"""
Below code is used to defined PyTreeString objects, which defines strings
as PyTree objects that can be propagated as a dynamic object in the PyTree
structure.

Obtained from ift/NIFTy/src/re/tree_math/pytree_string.py

# SPDX-License-Identifier: GPL-2.0+ OR BSD-2-Clause 
"""


def _unary_op(op, name=None):
    def unary_call(lhs):
        return op(lhs._str)

    name = op.__name__ if name is None else name
    unary_call.__name__ = f"__{name}__"
    return unary_call


def _binary_op(op, name=None):
    def binary_call(lhs, rhs):
        lhs = lhs._str if isinstance(lhs, PyTreeString) else lhs
        rhs = rhs._str if isinstance(rhs, PyTreeString) else rhs
        out = op(lhs, rhs)
        return PyTreeString(out) if isinstance(out, str) else out

    name = op.__name__ if name is None else name
    binary_call.__name__ = f"__{name}__"
    return binary_call


def _rev_binary_op(op, name=None):
    def binary_call(lhs, rhs):
        lhs = lhs._str if isinstance(lhs, PyTreeString) else lhs
        rhs = rhs._str if isinstance(rhs, PyTreeString) else rhs
        out = op(rhs, lhs)
        return PyTreeString(out) if isinstance(out, str) else out

    name = op.__name__ if name is None else name
    binary_call.__name__ = f"__r{name}__"
    return binary_call


def _fwd_rev_binary_op(op, name=None):
    return (_binary_op(op, name=name), _rev_binary_op(op, name=name))


@register_pytree_node_class
class PyTreeString:
    def __init__(self, str):
        self._str = str

    def tree_flatten(self):
        return ((), (self._str,))

    @classmethod
    def tree_unflatten(cls, aux, _):
        return cls(*aux)

    def __str__(self):
        return self._str

    def __repr__(self):
        return f"{self.__class__.__name__}({self._str!r})"

    __lt__ = _binary_op(operator.lt)
    __le__ = _binary_op(operator.le)
    __eq__ = _binary_op(operator.eq)
    __ne__ = _binary_op(operator.ne)
    __ge__ = _binary_op(operator.ge)
    __gt__ = _binary_op(operator.gt)

    __add__, __radd__ = _fwd_rev_binary_op(operator.add)
    __mul__, __rmul__ = _fwd_rev_binary_op(operator.mul)

    lower = _unary_op(str.lower)
    upper = _unary_op(str.upper)

    __hash__ = _unary_op(str.__hash__)

    startswith = _binary_op(str.startswith)


def hide_strings(a):
    return tree_map(lambda x: PyTreeString(x) if isinstance(x, str) else x, a)


def jax_zip(x: jax.typing.ArrayLike, y: jax.typing.ArrayLike) -> list[tuple]:
    """equivalent of zip function in Python"""

    assert x.shape[0] == y.shape[0], "lengths do not match."

    return tree_map(
        lambda xx, yy: jax.numpy.array([[xx[i], yy[i]] for i in range(x.shape[0])]),
        x,
        y,
    )


def jit_repeat(
    a: jax.typing.ArrayLike,
    repeats: jax.typing.ArrayLike,
    axis: Union[int, None],
    total_repeat_length: Union[int, None],
):
    """Jit-compiled version of jax.numpy.repeat."""
    return jax.jit(jax.numpy.repeat, static_argnames=["axis", "total_repeat_length"])(
        a, repeats, axis, total_repeat_length
    )
