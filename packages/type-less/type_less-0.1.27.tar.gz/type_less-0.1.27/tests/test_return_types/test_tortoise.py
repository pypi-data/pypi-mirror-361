from ..matching import validate_is_equivalent_type
import pytest
from type_less.inference import guess_return_type
from typing import Literal, TypedDict
from tortoise import Model, fields


class Cat(Model):
    color = fields.CharField(max_length=10)
    has_ears = fields.BooleanField()


# Test Chaining


@pytest.mark.asyncio
async def test_tortoise_model_chaining_first():
    async def func():
        return await Cat.filter(color="black").first()

    assert validate_is_equivalent_type(guess_return_type(func), Cat | None)


@pytest.mark.asyncio
async def test_tortoise_model_chaining_all():
    async def func():
        return await Cat.filter(color="black").all()

    assert validate_is_equivalent_type(guess_return_type(func), list[Cat])
