import importlib
import sys
import warnings

import pytest


@pytest.mark.parametrize("name", ["maxo.exceptions", "maxo.filters", "maxo.methods"])
def test_permanent_alias_imports_without_warnings(name: str) -> None:
    # aiogram aliases are permanent, warning about their removal would be a lie
    sys.modules.pop(name, None)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        importlib.import_module(name)
