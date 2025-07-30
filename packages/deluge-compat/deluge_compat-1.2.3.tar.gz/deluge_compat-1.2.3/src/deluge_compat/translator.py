"""Deluge to Python code translator."""

import re
from typing import Any


class DelugeTranslator:
    """Translates Deluge script syntax to Python code."""

    def __init__(self):
        self.indent_level = 0
        self.in_invokeurl = False
        self.in_sendmail = False
        self.brace_stack = []  # Track opening braces and their contexts

    def translate(self, deluge_code: str) -> str:
        """Translate Deluge code to Python code."""
        # Reset state for each translation
        self.indent_level = 0
        self.in_invokeurl = False
        self.in_sendmail = False
        self.brace_stack = []

        # Preprocess the code to handle } else { patterns
        preprocessed = self._preprocess_code(deluge_code)

        lines = preprocessed.split("\n")
        python_lines = []

        self._last_line = ""
        for line in lines:
            original_line = line.strip()
            if not original_line:
                continue

            translated = self._translate_line(original_line)
            if translated:
                python_lines.append(translated)

            self._last_line = original_line

        return "\n".join(python_lines)

    def _preprocess_code(self, code: str) -> str:
        """Preprocess Deluge code to handle special patterns."""
        # Handle inline } else { patterns by breaking them into separate lines
        code = re.sub(r"}\s*else\s*{", "}\nelse {", code)

        # Handle } else if { patterns
        code = re.sub(r"}\s*else\s+if\s*\([^)]*\)\s*{", lambda m: "}\n" + m.group(0)[1:], code)

        return code

    def _remove_inline_comments(self, line: str) -> str:
        """Remove inline comments but preserve // inside string literals."""
        in_string = False
        quote_char = None
        result = []

        i = 0
        while i < len(line):
            char = line[i]

            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    quote_char = char
                    result.append(char)
                elif char == "/" and i + 1 < len(line) and line[i + 1] == "/":
                    # Found // comment outside string, stop here
                    break
                elif char == "#":
                    # Found # comment outside string, stop here
                    break
                else:
                    result.append(char)
            else:
                result.append(char)
                if char == quote_char and (i == 0 or line[i - 1] != "\\"):
                    # End of string literal
                    in_string = False
                    quote_char = None

            i += 1

        return "".join(result).strip()

    def _translate_line(self, line: str) -> str:
        """Translate a single line of Deluge code."""
        line = line.strip()

        # Remove inline comments (but not // inside strings)
        line = self._remove_inline_comments(line)

        # Skip empty lines and comments
        if not line or line.startswith("//"):
            return ""

        # Handle multi-line comments
        if line.startswith("/*") or line.endswith("*/"):
            return ""

        # Handle closing braces first (decrease indent before processing)
        if line == "}":
            self.indent_level -= 1
            if self.brace_stack:
                self.brace_stack.pop()
            return ""

        # Handle control structures that end with opening brace
        if line.startswith("if(") or line.startswith("if "):
            result = self._translate_if(line)
            if line.rstrip().endswith("{"):
                self.indent_level += 1
                self.brace_stack.append("if")
            return result
        elif line.startswith("for each"):
            result = self._translate_for_each(line)
            if line.rstrip().endswith("{"):
                self.indent_level += 1
                self.brace_stack.append("for")
            return result
        elif line.startswith("while("):
            result = self._translate_while(line)
            if line.rstrip().endswith("{"):
                self.indent_level += 1
                self.brace_stack.append("while")
            return result
        elif line.startswith("else"):
            result = self._translate_else(line)
            if line.rstrip().endswith("{"):
                self.indent_level += 1
                self.brace_stack.append("else")
            return result

        # Handle standalone opening braces
        elif line == "{":
            self.indent_level += 1
            self.brace_stack.append("block")
            return ""

        # Handle invokeurl blocks (check this early, before error detection)
        elif line.startswith("invokeurl"):
            return self._translate_invokeurl_start(line)
        elif line == "];":
            return self._translate_invokeurl_end()
        elif self.in_invokeurl and ":" in line:
            return self._translate_invokeurl_param(line)

        # Handle sendmail blocks
        elif line.startswith("sendmail"):
            return self._translate_sendmail_start(line)
        elif line == "[" and hasattr(self, "_last_line") and self._last_line.startswith("sendmail"):
            self.in_sendmail = True
            return ""  # Skip the opening bracket
        elif line == "]" and self.in_sendmail:
            return self._translate_sendmail_end()
        elif self.in_sendmail and ":" in line:
            return self._translate_sendmail_param(line)

        # Handle function calls and statements
        elif line.startswith("info "):
            return self._translate_info(line)
        elif line.startswith("return"):
            return self._translate_return(line)

        # Handle variable declarations and assignments
        elif "=" in line and not any(op in line for op in ["==", "!=", "<=", ">="]):
            # Check if this is an invokeurl assignment
            if "invokeurl" in line:
                return self._translate_invokeurl_start(line)
            else:
                return self._translate_assignment(line)

        # Handle statements ending with semicolon
        elif line.endswith(";"):
            return self._translate_statement(line)

        # If we reach here, the line couldn't be translated
        # But skip error for invokeurl context or comment lines
        elif (
            line.strip()
            and not line.startswith("//")
            and not line.startswith("#")
            and not self.in_invokeurl
        ):
            raise ValueError(f"Unable to translate Deluge syntax: '{line}'")

        return ""

    def _get_indent(self) -> str:
        """Get current indentation string."""
        return "    " * self.indent_level

    def _translate_assignment(self, line: str) -> str:
        """Translate variable assignment."""
        line = line.rstrip(";")

        # Handle special constructors
        if "Map()" in line:
            line = line.replace("Map()", "Map()")
        elif "List()" in line:
            line = line.replace("List()", "List()")
        elif "list()" in line:
            line = line.replace("list()", "List()")
        elif "Collection()" in line:
            line = line.replace("Collection()", "Map()")

        # Handle string literals - wrap in deluge_string
        line = self._wrap_string_literals(line)

        # Handle method calls on strings
        line = self._translate_string_methods(line)

        # Handle logical operators
        line = self._translate_logical_operators(line)

        return self._get_indent() + line

    def _translate_if(self, line: str) -> str:
        """Translate if statement."""
        # Handle both 'if(' and 'if ' syntax
        if line.startswith("if("):
            # Extract condition from if(condition) {
            paren_start = line.find("(")
            paren_end = line.rfind(")")
            if paren_start != -1 and paren_end != -1:
                condition = line[paren_start + 1 : paren_end]
            else:
                condition = line[3:].rstrip("{").strip()
        else:
            # Handle 'if ' syntax
            condition = line[3:].rstrip("{").strip()

        # Translate condition
        condition = self._translate_condition(condition)

        return self._get_indent() + f"if {condition}:"

    def _translate_else(self, line: str) -> str:
        """Translate else statement."""
        line_clean = line.rstrip("{").strip()

        # else/elif should be at the same level as the corresponding if
        # When we encounter else, we want to be at the current indent level
        # (which should be correct after processing the closing brace)
        indent_str = self._get_indent()

        if line_clean == "else":
            return indent_str + "else:"
        elif line_clean.startswith("else if"):
            # else if case
            condition = line_clean[7:].strip()  # Remove 'else if'
            if condition.startswith("(") and condition.endswith(")"):
                condition = condition[1:-1]
            condition = self._translate_condition(condition)
            return indent_str + f"elif {condition}:"
        else:
            return indent_str + "else:"

    def _translate_for_each(self, line: str) -> str:
        """Translate for each loop."""
        # Extract variable and iterable from 'for each var in iterable'
        line_clean = line.rstrip("{").strip()
        match = re.match(r"for each\s+(\w+)\s+in\s+(.+)", line_clean)
        if match:
            var_name = match.group(1)
            iterable = match.group(2).strip()
            return self._get_indent() + f"for {var_name} in {iterable}:"
        return self._get_indent() + line_clean + ":"

    def _translate_while(self, line: str) -> str:
        """Translate while loop."""
        condition = line[6:].rstrip("{").strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1]
        condition = self._translate_condition(condition)
        return self._get_indent() + f"while {condition}:"

    def _translate_condition(self, condition: str) -> str:
        """Translate condition expressions."""
        # Handle method calls
        condition = self._translate_string_methods(condition)

        # Handle null checks
        condition = condition.replace("== NULL", "is None")
        condition = condition.replace("!= NULL", "is not None")
        condition = condition.replace("== null", "is None")
        condition = condition.replace("!= null", "is not None")

        # Handle boolean values
        condition = condition.replace(" true", " True")
        condition = condition.replace(" false", " False")

        # Handle logical operators
        condition = condition.replace("&&", " and ")
        condition = condition.replace("||", " or ")

        return condition

    def _translate_invokeurl_start(self, line: str) -> str:
        """Start of invokeurl block."""
        # Extract variable assignment if present
        if "=" in line:
            var_name = line.split("=")[0].strip()
            self.in_invokeurl = True
            return self._get_indent() + f"{var_name} = _invokeurl({{"
        else:
            self.in_invokeurl = True
            return self._get_indent() + "_invokeurl({"

    def _translate_invokeurl_param(self, line: str) -> str:
        """Translate invokeurl parameter."""
        line = line.strip()
        if line.endswith(","):
            line = line[:-1]

        # Split on first ':'
        parts = line.split(":", 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()

            # Wrap string values in quotes if not already quoted
            if not (value.startswith('"') and value.endswith('"')):
                if not value.startswith("(") and not value.isdigit():
                    # Check if it's a variable reference
                    if not any(c in value for c in [".", "(", ")", "+", "-", "*", "/"]):
                        value = f'"{value}"'

            return self._get_indent() + f'    "{key}": {value},'

        return self._get_indent() + f"    {line},"

    def _translate_invokeurl_end(self) -> str:
        """End of invokeurl block."""
        self.in_invokeurl = False
        return self._get_indent() + "})"

    def _translate_info(self, line: str) -> str:
        """Translate info statement."""
        content = line[5:].rstrip(";").strip()
        return self._get_indent() + f"info({content})"

    def _translate_return(self, line: str) -> str:
        """Translate return statement."""
        content = line[6:].rstrip(";").strip()
        content = self._wrap_string_literals(content)
        return self._get_indent() + f"return {content}"

    def _translate_statement(self, line: str) -> str:
        """Translate general statement."""
        line = line.rstrip(";")
        line = self._translate_string_methods(line)
        line = self._translate_logical_operators(line)
        return self._get_indent() + line

    def _translate_logical_operators(self, text: str) -> str:
        """Translate logical operators from Deluge to Python."""
        text = text.replace("&&", " and ")
        text = text.replace("||", " or ")
        return text

    def _wrap_string_literals(self, text: str) -> str:
        """Wrap string literals with deluge_string() calls."""

        # Find string literals (content within quotes)
        def replace_string(match):
            quote_char = match.group(1)
            content = match.group(2)
            return f"deluge_string({quote_char}{content}{quote_char})"

        # Handle both single and double quoted strings
        text = re.sub(r'(["\'])([^"\']*)\1', replace_string, text)
        return text

    def _translate_string_methods(self, text: str) -> str:
        """Translate string method calls to use Deluge string methods."""
        # Common method translations
        method_map = {
            ".trim()": ".trim()",
            ".length()": ".length()",
            ".contains(": ".contains(",
            ".startsWith(": ".startsWith(",
            ".endsWith(": ".endsWith(",
            ".toLowerCase()": ".toLowerCase()",
            ".toUpperCase()": ".toUpperCase()",
            ".substring(": ".substring(",
            ".subString(": ".subString(",
            ".subText(": ".subText(",
            ".indexOf(": ".indexOf(",
            ".lastIndexOf(": ".lastIndexOf(",
            ".replaceAll(": ".replaceAll(",
            ".replaceFirst(": ".replaceFirst(",
            ".toList(": ".toList(",
            ".toMap()": ".toMap()",
            ".size()": ".size()",
            ".isEmpty()": ".isEmpty()",
            ".get(": ".get(",
            ".put(": ".put(",
            ".add(": ".add(",
            ".remove(": ".remove(",
            ".clear()": ".clear()",
        }

        for deluge_method, python_method in method_map.items():
            text = text.replace(deluge_method, python_method)

        return text

    def _translate_sendmail_start(self, line: str) -> str:
        """Start translating a sendmail block."""
        # Don't set in_sendmail yet - wait for the opening bracket
        self.sendmail_params = {}

        # Return the beginning of sendmail function call
        return "sendmail("

    def _translate_sendmail_param(self, line: str) -> str:
        """Translate a sendmail parameter line."""
        line = line.strip()

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes from key if present
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]

            # Handle value processing
            if value.startswith('"') and value.endswith('"'):
                # String literal
                processed_value = value
            else:
                # Expression that needs evaluation
                processed_value = self._translate_string_methods(value)

            # Use **kwargs syntax to handle Python keywords like 'from'
            return f'    **{{"{key}": {processed_value}}},'

        return ""

    def _translate_sendmail_end(self) -> str:
        """End translating a sendmail block."""
        self.in_sendmail = False
        return ")"


def _invokeurl(params: dict[str, Any]) -> Any:  # pyright: ignore[reportUnusedFunction]
    """Execute an HTTP request based on invokeurl parameters."""
    from .functions import getUrl, postUrl

    url = params.get("url", "")
    request_type = params.get("type", "GET").upper()
    headers = params.get("headers", {})
    parameters = params.get("parameters", {})

    if request_type == "GET":
        return getUrl(url, headers=headers)
    elif request_type == "POST":
        return postUrl(url, body=parameters, headers=headers)
    else:
        # For other HTTP methods, use requests directly
        try:
            import requests

            method = request_type.lower()
            if hasattr(requests, method):
                response = getattr(requests, method)(url, json=parameters, headers=headers)
                return response.text
            else:
                return "Unsupported HTTP method"
        except ImportError:
            return "Requests module not available"
