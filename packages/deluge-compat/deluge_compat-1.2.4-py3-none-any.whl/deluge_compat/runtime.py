"""Deluge script runtime environment."""

from typing import Any

from .functions import BUILTIN_FUNCTIONS
from .salesiq.functions import visitorsession_get, visitorsession_set
from .translator import DelugeTranslator, _invokeurl
from .types import deluge_string


class DelugeRuntime:
    """Runtime environment for executing Deluge scripts."""

    def __init__(self):
        self.translator = DelugeTranslator()
        self.context = self._create_base_context()

    def _create_base_context(self) -> dict[str, Any]:
        """Create the base execution context with built-in functions and types."""
        context = BUILTIN_FUNCTIONS.copy()

        # Add built-in variables and constants
        context.update(
            {
                "NULL": None,
                "null": None,
                "true": True,
                "false": False,
                "True": True,
                "False": False,
                "deluge_string": deluge_string,
                "_invokeurl": _invokeurl,
                # Add zoho namespace for SalesIQ compatibility
                "zoho": self._create_zoho_namespace(),
            }
        )

        return context

    def _create_zoho_namespace(self) -> dict[str, Any]:
        """Create the zoho namespace with SalesIQ functions."""
        return {
            "salesiq": {
                "visitorsession": {
                    "get": visitorsession_get,
                    "set": visitorsession_set,
                }
            },
            "adminuserid": "admin@example.com",  # Default admin user for mocking
        }

    def update_context(self, additional_context: dict[str, Any]) -> None:
        """Add additional variables to the execution context."""
        self.context.update(additional_context)

    def execute(self, deluge_code: str) -> Any:
        """Execute Deluge code and return the result."""
        try:
            # Translate Deluge code to Python
            python_code = self.translator.translate(deluge_code)

            # Debug: print translated code (disabled for tests)
            # print("=== Translated Python Code ===")
            # print(python_code)
            # print("==============================")

            # Create a clean execution environment
            exec_globals = self.context.copy()
            exec_locals = {}

            # Wrap the code in a function to handle return statements
            # Handle empty scripts by adding 'pass' statement
            indented_code = self._indent_code(python_code, 1)
            if not indented_code.strip():
                indented_code = "    pass"

            wrapped_code = f"""
def _deluge_script():
{indented_code}

_result = _deluge_script()
"""

            # Execute the wrapped Python code
            exec(wrapped_code, exec_globals, exec_locals)

            # Return the result
            return exec_locals.get("_result", None)

        except Exception as e:
            raise DelugeRuntimeError(f"Error executing Deluge script: {e}") from e

    def _indent_code(self, code: str, levels: int) -> str:
        """Add indentation to code."""
        indent = "    " * levels
        lines = code.split("\n")
        indented_lines = []
        for line in lines:
            if line.strip():
                indented_lines.append(indent + line)
            else:
                indented_lines.append("")
        return "\n".join(indented_lines)

    def execute_file(self, file_path: str, **context) -> Any:
        """Execute Deluge code from a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                deluge_code = f.read()

            if context:
                self.update_context(context)

            return self.execute(deluge_code)

        except FileNotFoundError as e:
            raise DelugeRuntimeError(f"Deluge script file not found: {file_path}") from e
        except Exception as e:
            raise DelugeRuntimeError(f"Error reading Deluge script file: {e}") from e


class DelugeRuntimeError(Exception):
    """Exception raised during Deluge script execution."""

    pass


def run_deluge_file(file_path: str, **context) -> Any:
    """Convenience function to run a Deluge script file."""
    runtime = DelugeRuntime()
    return runtime.execute_file(file_path, **context)


def run_deluge_script(script: str, **context) -> Any:
    """Convenience function to run a Deluge script string."""
    runtime = DelugeRuntime()
    if context:
        runtime.update_context(context)
    return runtime.execute(script)
