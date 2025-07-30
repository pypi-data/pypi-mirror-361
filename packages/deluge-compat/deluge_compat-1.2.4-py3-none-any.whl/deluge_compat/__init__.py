"""Deluge Compatibility Layer for Python.

This module provides compatibility for running Deluge scripts in Python.
"""

__version__ = "1.2.4"

from typing import Any

from .runtime import DelugeRuntime
from .translator import DelugeTranslator
from .types import DelugeString, List, Map, deluge_string

__all__ = [
    "DelugeRuntime",
    "DelugeTranslator",
    "Map",
    "List",
    "DelugeString",
    "deluge_string",
    "run_deluge_script",
    "translate_deluge_to_python",
]


def run_deluge_script(script: str, **context) -> Any:
    """Execute a Deluge script string in Python.

    Args:
        script: The Deluge script code as a string
        **context: Additional variables to make available in the script context

    Returns:
        The result of executing the script
    """
    runtime = DelugeRuntime()
    runtime.update_context(context)
    return runtime.execute(script)


def translate_deluge_to_python(
    deluge_script: str, wrap_in_function: bool = True, pep723_compatible: bool = True
) -> str:
    """Translate a Deluge script to Python code.

    Args:
        deluge_script: The Deluge script code as a string
        wrap_in_function: If True, wraps the code in a function for execution (default: True)
        pep723_compatible: If True, generates PEP 723 compatible script (default: True)

    Returns:
        The translated Python code as a string

    Example:
        >>> deluge_code = '''
        ... result = Map();
        ... result.put("message", "Hello World");
        ... return result;
        ... '''
        >>> python_code = translate_deluge_to_python(deluge_code)
        >>> print(python_code)
    """
    translator = DelugeTranslator()
    python_code = translator.translate(deluge_script)

    if wrap_in_function:
        # Add PEP 723 header if requested
        pep723_header = ""
        if pep723_compatible:
            pep723_header = """# /// script
# dependencies = [
#   "deluge-compat"
# ]
# ///

"""

        # Add necessary imports
        imports = """from deluge_compat import Map, List, DelugeString, deluge_string
from deluge_compat.functions import *

"""
        # Wrap in a function
        indented_code = "\n".join(
            f"    {line}" if line.strip() else "" for line in python_code.split("\n")
        )
        wrapped_code = f"""{pep723_header}{imports}def deluge_script():
{indented_code}

if __name__ == "__main__":
    result = deluge_script()
    if result is not None:
        print(result)
"""
        return wrapped_code
    else:
        return python_code
