from entrypoints.bootstrap import (
    inject_dependencies
)
import pytest

def add_callable(a, b, c):
    return a + b + c

def  test_inject_dependencies():
    add_dependencies = {
        "a": 1,
        "b": 1,
        "c": 1,
    }
    handler_partial = inject_dependencies(
        handler=add_callable,
        dependencies=add_dependencies
    )

    assert handler_partial() == 3

def test_inject_dependencies_missing_one_argument():
    add_dependencies = {
        "a": 1,
        "b": 1,
    }
    handler_partial = inject_dependencies(
        handler=add_callable,
        dependencies=add_dependencies
    )
    with pytest.raises(TypeError):
        handler_partial()
