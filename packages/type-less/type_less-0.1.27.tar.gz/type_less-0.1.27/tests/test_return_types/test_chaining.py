from ..matching import validate_is_equivalent_type
from type_less.inference import guess_return_type
from typing import Awaitable, Literal, TypedDict, Type, TypeVar, Union


class Class1:
    name: str = "test"

    def func2(self):
        return self.name


def func1():
    return Class1()


def test_chaining_functions():
    def func():
        return func1().func2()

    assert guess_return_type(func) == str
