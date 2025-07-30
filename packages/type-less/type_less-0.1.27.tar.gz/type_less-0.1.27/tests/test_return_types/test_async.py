import pytest
from ..external import AsyncDonkey as Dinkey
from ..matching import validate_is_equivalent_type
from type_less.inference import guess_return_type
from typing import Any, Awaitable, Callable, Generator, Literal, Protocol, Self, TypedDict, Type, TypeVar


MODEL = TypeVar("MODEL", bound="Animal")
class Animal:
    @classmethod
    async def create(cls: Type[MODEL]) -> MODEL:
        return cls()
    

class Cat(Animal):
    color: Literal["black", "orange"]
    has_ears: bool
    

class Collar:
    cat: Awaitable[Cat]


# Async

async def get_cat_async() -> Cat:
    return Cat(color="black", has_ears=True)

@pytest.mark.asyncio
async def test_guess_return_type_follow_function_return_async():
    class TheCatReturns(TypedDict):
        color: Literal["black", "orange"]
        has_ears: bool

    async def func():
        cat = await get_cat_async()
        return {
            "color": cat.color,
            "has_ears": cat.has_ears,
        }
    
    assert validate_is_equivalent_type(guess_return_type(func), TheCatReturns)

# Static method

class FeatureA:
    thingo: int

    @staticmethod
    async def run_me() -> tuple["FeatureA", "FeatureB"]:
        return FeatureA(), FeatureB()


class FeatureB:
    thingo: bool


@pytest.mark.asyncio
async def test_guess_return_type_follow_function_return_async():
    async def func():
        fa, fb = await FeatureA.run_me()
        return fb, fa
    
    assert validate_is_equivalent_type(guess_return_type(func), tuple[FeatureB, FeatureA])

# Inherited


@pytest.mark.asyncio
async def test_inherited_typevar_async_method():
    async def func():
        cat = await Cat.create()
        return cat
    
    assert validate_is_equivalent_type(guess_return_type(func), Cat)

@pytest.mark.asyncio
async def test_awaitable_member_variable():
    async def func():
        collar = Collar()
        cat = await collar.cat
        return cat
    
    assert validate_is_equivalent_type(guess_return_type(func), Cat)


# External


@pytest.mark.asyncio
async def test_external_static_method_quoted_type_renamed():
    async def func():
        donkey, donkey2 = await Dinkey.get_by_saddle(10)
        return donkey, donkey2
    
    assert validate_is_equivalent_type(guess_return_type(func), tuple[Dinkey, Dinkey])

# Complex Generator - tortoise ORM check

T_co = TypeVar("T_co", covariant=True)
MODEL = TypeVar("MODEL", bound="Model")

class QuerySetSingle(Protocol[T_co]):
    def __await__(self) -> Generator[Any, None, T_co]: ...  # pragma: nocoverage

class QuerySet(Protocol[T_co]):
    def __await__(self) -> Generator[Any, None, list[T_co]]: ...  # pragma: nocoverage

class Model:
    @classmethod
    def get(cls) -> QuerySetSingle[Self]:
        return QuerySetSingle[Self]()
    
    @classmethod
    def all(cls) -> QuerySet[Self]:
        return QuerySet[Self]()

class Tortoise(Model):
    id: int
    name: str

@pytest.mark.asyncio
async def test_tortoise_queryset_single():
    async def func():
        model = await Tortoise.get()
        return model
    
    assert validate_is_equivalent_type(guess_return_type(func), Tortoise)

@pytest.mark.asyncio
async def test_tortoise_queryset():
    async def func():
        models = await Tortoise.all()
        return models
    
    assert validate_is_equivalent_type(guess_return_type(func), list[Tortoise])

# Decorated

CLS = TypeVar("CLS")
def decorated(*args, **kwargs) -> Callable[[Type[CLS]], Type[CLS]]:
    def decorator(cls: Type[CLS]) -> Type[CLS]:
        return cls
    return decorator

@decorated("test")
class DecoratedTortoise(Model):
    id: int
    name: str

@pytest.mark.asyncio
async def test_decorated_tortoise_queryset_single():
    async def func():
        models = await DecoratedTortoise.get()
        return models
    
    assert validate_is_equivalent_type(guess_return_type(func), DecoratedTortoise)

@pytest.mark.asyncio
async def test_decorated_tortoise_queryset():
    async def func():
        models = await DecoratedTortoise.all()
        return models
    
    assert validate_is_equivalent_type(guess_return_type(func), list[DecoratedTortoise])