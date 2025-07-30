"""Test Deluge runtime environment."""

import pytest

from deluge_compat.runtime import DelugeRuntime, DelugeRuntimeError, run_deluge_script
from deluge_compat.types import List, Map


class TestDelugeRuntime:
    """Test the Deluge runtime environment."""

    def setup_method(self):
        """Set up runtime for each test."""
        self.runtime = DelugeRuntime()

    def test_runtime_creation(self):
        """Test runtime creation and base context."""
        assert self.runtime.context is not None
        assert "Map" in self.runtime.context
        assert "List" in self.runtime.context
        assert "info" in self.runtime.context
        assert "getUrl" in self.runtime.context

    def test_update_context(self):
        """Test updating runtime context."""
        self.runtime.update_context({"custom_var": "custom_value"})
        assert self.runtime.context["custom_var"] == "custom_value"

    def test_simple_script_execution(self):
        """Test execution of a simple script."""
        script = """
        result = Map();
        result.put("message", "Hello World");
        return result;
        """

        result = self.runtime.execute(script)
        assert isinstance(result, Map)
        assert result.get("message") == "Hello World"

    def test_script_with_variables(self):
        """Test script execution with context variables."""
        script = """
        greeting = "Hello " + name + "!";
        result = Map();
        result.put("greeting", greeting);
        return result;
        """

        self.runtime.update_context({"name": "Alice"})
        result = self.runtime.execute(script)

        assert isinstance(result, Map)
        assert "Hello Alice!" in str(result.get("greeting"))

    def test_list_operations(self):
        """Test script with list operations."""
        script = """
        numbers = List();
        numbers.add(1);
        numbers.add(2);
        numbers.add(3);

        sum = 0;
        for each num in numbers {
            sum = sum + num;
        }

        result = Map();
        result.put("numbers", numbers);
        result.put("sum", sum);
        return result;
        """

        result = self.runtime.execute(script)
        assert isinstance(result, Map)
        assert result.get("sum") == 6
        assert isinstance(result.get("numbers"), List)
        assert result.get("numbers").size() == 3

    def test_string_operations(self):
        """Test script with string operations."""
        script = """
        text = "Hello World";
        result = Map();

        result.put("original", text);
        result.put("upper", text.toUpperCase());
        result.put("length", text.length());
        result.put("contains_hello", text.contains("Hello"));

        return result;
        """

        result = self.runtime.execute(script)
        assert isinstance(result, Map)
        assert result.get("upper") == "HELLO WORLD"
        assert result.get("length") == 11
        assert result.get("contains_hello") is True

    def test_conditional_logic(self):
        """Test script with conditional logic."""
        script = """
        age = 25;
        result = Map();

        if(age >= 18) {
            status = "adult";
        }

        result.put("age", age);
        result.put("status", status);
        return result;
        """

        result = self.runtime.execute(script)
        assert isinstance(result, Map)
        assert result.get("age") == 25
        assert result.get("status") == "adult"

    def test_function_calls(self):
        """Test script with built-in function calls."""
        script = """
        result = Map();

        encoded = base64Encode("Hello World");
        decoded = base64Decode(encoded);

        result.put("encoded", encoded);
        result.put("decoded", decoded);
        result.put("match", decoded.equals("Hello World"));

        return result;
        """

        result = self.runtime.execute(script)
        assert isinstance(result, Map)
        assert result.get("decoded") == "Hello World"

    def test_math_operations(self):
        """Test script with mathematical operations."""
        script = """
        result = Map();

        result.put("abs_neg", abs(-5));
        result.put("power", power(2, 3));
        result.put("min", min(10, 5));
        result.put("max", max(10, 5));

        return result;
        """

        result = self.runtime.execute(script)
        assert isinstance(result, Map)
        assert result.get("abs_neg") == 5
        assert result.get("power") == 8
        assert result.get("min") == 5
        assert result.get("max") == 10

    def test_error_handling(self):
        """Test error handling in runtime."""
        # Test syntax error
        with pytest.raises(DelugeRuntimeError):
            self.runtime.execute("invalid syntax $$%")

        # Test runtime error
        with pytest.raises(DelugeRuntimeError):
            self.runtime.execute("undefined_variable.method();")

    def test_info_logging(self, capsys):
        """Test info function logging."""
        script = """
        info "Test message";
        info "Another message", 123;
        return "done";
        """

        result = self.runtime.execute(script)
        captured = capsys.readouterr()

        assert "INFO: Test message" in captured.out
        assert "INFO: Another message 123" in captured.out
        assert result == "done"


class TestConvenienceFunctions:
    """Test convenience functions for running scripts."""

    def test_run_deluge_script_basic(self):
        """Test run_deluge_script convenience function."""
        script = """
        message = "Hello from convenience function!";
        result = Map();
        result.put("message", message);
        return result;
        """

        result = run_deluge_script(script)
        assert isinstance(result, Map)
        assert "Hello from convenience function!" in str(result.get("message"))

    def test_run_deluge_script_with_context(self):
        """Test run_deluge_script with context variables."""
        script = """
        result = Map();
        result.put("name", name);
        result.put("age", age);
        result.put("greeting", "Hello " + name);
        return result;
        """

        result = run_deluge_script(script, name="Bob", age=30)
        assert isinstance(result, Map)
        assert result.get("name") == "Bob"
        assert result.get("age") == 30
        assert "Hello Bob" in str(result.get("greeting"))

    def test_empty_script(self):
        """Test execution of empty script."""
        # Test empty script
        result = run_deluge_script("")
        assert result is None

        # Test whitespace-only script
        result = run_deluge_script("   \n  \n  ")
        assert result is None

        # Test comment-only script
        result = run_deluge_script("// Just a comment")
        assert result is None

    def test_script_without_return(self):
        """Test script without explicit return."""
        script = """
        x = 42;
        y = "test";
        """

        result = run_deluge_script(script)
        # Should return None since no explicit return
        assert result is None

    def test_multiple_operations(self):
        """Test script with multiple complex operations."""
        script = """
        // Create some test data
        users = List();
        users.add("Alice");
        users.add("Bob");
        users.add("Charlie");

        // Process the data
        result = Map();
        processed_users = List();

        for each user in users {
            if(user.length() > 3) {
                upper_user = user.toUpperCase();
                processed_users.add(upper_user);
            }
        }

        result.put("original_count", users.size());
        result.put("processed_count", processed_users.size());
        result.put("processed_users", processed_users);

        return result;
        """

        result = run_deluge_script(script)
        assert isinstance(result, Map)
        assert result.get("original_count") == 3
        assert result.get("processed_count") == 2  # Alice and Charlie
        assert isinstance(result.get("processed_users"), List)


class TestRuntimeErrorCases:
    """Test various error conditions in the runtime."""

    def test_invalid_method_call(self):
        """Test calling invalid method."""
        script = """
        text = "hello";
        text.nonexistentMethod();
        """

        with pytest.raises(DelugeRuntimeError):
            run_deluge_script(script)

    def test_undefined_variable(self):
        """Test using undefined variable."""
        script = """
        result = undefined_variable;
        """

        with pytest.raises(DelugeRuntimeError):
            run_deluge_script(script)

    def test_type_error(self):
        """Test type-related errors."""
        script = """
        number = 42;
        result = number.toUpperCase();  # Number doesn't have toUpperCase
        """

        with pytest.raises(DelugeRuntimeError):
            run_deluge_script(script)
