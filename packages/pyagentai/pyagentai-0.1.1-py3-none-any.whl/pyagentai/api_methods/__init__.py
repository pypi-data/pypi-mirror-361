"""
Auto-import all API method modules to trigger their decorators.
This is required to add API methods to the AgentAIClient class.
"""

import importlib
import pathlib
import pkgutil

pkg_path = pathlib.Path(__file__).parent
for mod in pkgutil.iter_modules([str(pkg_path)]):
    importlib.import_module(f"{__name__}.{mod.name}")
