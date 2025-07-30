"""Test the translation API functionality."""

from deluge_compat import translate_deluge_to_python


class TestTranslationAPI:
    """Test the translate_deluge_to_python function."""

    def test_simple_translation_with_wrapper(self):
        """Test translation with function wrapper."""
        deluge_script = """
        result = Map();
        result.put("key", "value");
        return result;
        """

        python_code = translate_deluge_to_python(deluge_script)

        # Check PEP 723 header
        assert "# /// script" in python_code
        assert "# dependencies = [" in python_code
        assert '#   "deluge-compat"' in python_code

        # Check imports are included
        assert "from deluge_compat import" in python_code
        assert "from deluge_compat.functions import *" in python_code

        # Check function wrapper
        assert "def deluge_script():" in python_code
        assert 'if __name__ == "__main__":' in python_code

        # Check translated code
        assert "result = Map()" in python_code
        assert 'result.put("key", "value")' in python_code
        assert "return result" in python_code

    def test_translation_without_wrapper(self):
        """Test translation without function wrapper."""
        deluge_script = """
        x = 42;
        y = "test";
        result = x + y.length();
        """

        python_code = translate_deluge_to_python(deluge_script, wrap_in_function=False)

        # No imports or wrapper
        assert "from deluge_compat import" not in python_code
        assert "def deluge_script():" not in python_code

        # Just the translated code
        assert "x = 42" in python_code
        assert 'y = deluge_string("test")' in python_code
        assert "result = x + y.length()" in python_code

    def test_translation_with_control_structures(self):
        """Test translation of control structures."""
        deluge_script = """
        for each item in items {
            if(item > 10) {
                big_items.add(item);
            } else {
                small_items.add(item);
            }
        }
        """

        python_code = translate_deluge_to_python(deluge_script, wrap_in_function=False)

        assert "for item in items:" in python_code
        assert "if item > 10:" in python_code
        assert "big_items.add(item)" in python_code
        assert "else:" in python_code
        assert "small_items.add(item)" in python_code

    def test_translation_preserves_string_literals(self):
        """Test that string literals are wrapped properly."""
        deluge_script = """
        message = "Hello World";
        url = "https://example.com";
        """

        python_code = translate_deluge_to_python(deluge_script, wrap_in_function=False)

        assert 'message = deluge_string("Hello World")' in python_code
        assert 'url = deluge_string("https://example.com")' in python_code

    def test_empty_script_translation(self):
        """Test translation of empty script."""
        python_code = translate_deluge_to_python("")

        # Should still have wrapper structure
        assert "def deluge_script():" in python_code
        assert "from deluge_compat import" in python_code

    def test_translation_with_comments(self):
        """Test that comments are handled correctly."""
        deluge_script = """
        // This is a comment
        x = 10; // Inline comment
        // Another comment
        y = 20;
        """

        python_code = translate_deluge_to_python(deluge_script, wrap_in_function=False)

        # Comments should be removed
        assert "This is a comment" not in python_code
        assert "Inline comment" not in python_code
        assert "Another comment" not in python_code

        # Code should be preserved
        assert "x = 10" in python_code
        assert "y = 20" in python_code

    def test_translation_without_pep723(self):
        """Test translation without PEP 723 header."""
        deluge_script = """
        result = Map();
        result.put("test", "value");
        return result;
        """

        python_code = translate_deluge_to_python(deluge_script, pep723_compatible=False)

        # Should not have PEP 723 header
        assert "# /// script" not in python_code
        assert "# dependencies = [" not in python_code

        # Should still have imports and wrapper
        assert "from deluge_compat import" in python_code
        assert "def deluge_script():" in python_code

    def test_translation_with_all_options(self):
        """Test translation with various option combinations."""
        deluge_script = "x = 42;"

        # Raw code without wrapper and without PEP 723
        raw_code = translate_deluge_to_python(
            deluge_script, wrap_in_function=False, pep723_compatible=False
        )
        assert "x = 42" in raw_code
        assert "# /// script" not in raw_code
        assert "def deluge_script():" not in raw_code

        # Wrapped code without PEP 723
        wrapped_no_pep723 = translate_deluge_to_python(
            deluge_script, wrap_in_function=True, pep723_compatible=False
        )
        assert "x = 42" in wrapped_no_pep723
        assert "# /// script" not in wrapped_no_pep723
        assert "def deluge_script():" in wrapped_no_pep723
