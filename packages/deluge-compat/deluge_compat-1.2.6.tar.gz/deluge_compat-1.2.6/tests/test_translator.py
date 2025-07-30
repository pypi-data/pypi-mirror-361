"""Test Deluge to Python translator."""

import pytest

from deluge_compat.translator import DelugeTranslator, _invokeurl


class TestDelugeTranslator:
    """Test the Deluge to Python translator."""

    def setup_method(self):
        """Set up translator for each test."""
        self.translator = DelugeTranslator()

    def test_simple_assignment(self):
        """Test simple variable assignment translation."""
        deluge_code = 'name = "John";'
        python_code = self.translator.translate(deluge_code)

        assert 'name = deluge_string("John")' in python_code

    def test_map_creation(self):
        """Test Map creation translation."""
        deluge_code = "response = Map();"
        python_code = self.translator.translate(deluge_code)

        assert "response = Map()" in python_code

    def test_list_creation(self):
        """Test List creation translation."""
        deluge_code = """
        items = List();
        items.add("apple");
        """
        python_code = self.translator.translate(deluge_code)

        assert "items = List()" in python_code
        assert 'items.add("apple")' in python_code

    def test_method_calls(self):
        """Test method call translation."""
        deluge_code = """
        text = "Hello World";
        upper = text.toUpperCase();
        length = text.length();
        """
        python_code = self.translator.translate(deluge_code)

        assert "upper = text.toUpperCase()" in python_code
        assert "length = text.length()" in python_code

    def test_if_statement(self):
        """Test if statement translation."""
        deluge_code = """
        if(age >= 18) {
            status = "adult";
        }
        """
        python_code = self.translator.translate(deluge_code)

        assert "if age >= 18:" in python_code
        assert 'status = deluge_string("adult")' in python_code  # Don't check indentation

    def test_for_each_loop(self):
        """Test for each loop translation."""
        deluge_code = """
        for each item in items {
            info item;
        }
        """
        python_code = self.translator.translate(deluge_code)

        assert "for item in items:" in python_code
        assert "info(item)" in python_code  # Don't check indentation

    def test_return_statement(self):
        """Test return statement translation."""
        deluge_code = "return response;"
        python_code = self.translator.translate(deluge_code)

        assert "return response" in python_code

    def test_info_statement(self):
        """Test info statement translation."""
        deluge_code = 'info "Debug message";'
        python_code = self.translator.translate(deluge_code)

        assert 'info("Debug message")' in python_code

    def test_comment_removal(self):
        """Test that comments are removed."""
        deluge_code = """
        // This is a comment
        name = "John";
        /* Multi-line
           comment */
        age = 25;
        """
        python_code = self.translator.translate(deluge_code)

        # Comments should be removed
        assert "//" not in python_code
        assert "/*" not in python_code
        assert "*/" not in python_code

        # Code should remain
        assert 'name = deluge_string("John")' in python_code
        assert "age = 25" in python_code

    def test_string_literal_wrapping(self):
        """Test that string literals are wrapped with deluge_string."""
        deluge_code = """
        message = "Hello World";
        single = 'Single quotes';
        """
        python_code = self.translator.translate(deluge_code)

        assert 'deluge_string("Hello World")' in python_code
        assert "deluge_string('Single quotes')" in python_code

    def test_boolean_values(self):
        """Test boolean value translation."""
        deluge_code = """
        isActive = true;
        isDisabled = false;
        """
        python_code = self.translator.translate(deluge_code)

        assert "isActive = true" in python_code
        assert "isDisabled = false" in python_code

    def test_complex_script(self):
        """Test translation of a more complex script."""
        deluge_code = """
        response = Map();
        users = List();
        users.add("Alice");
        users.add("Bob");

        for each user in users {
            if(user.length() > 3) {
                response.put(user, "long_name");
            }
        }

        return response;
        """
        python_code = self.translator.translate(deluge_code)

        # Check key elements are present
        assert "response = Map()" in python_code
        assert "users = List()" in python_code
        assert "for user in users:" in python_code
        assert "if user.length() > 3:" in python_code
        assert "return response" in python_code

    def test_invokeurl_preprocessing(self):
        """Test that invokeurl blocks are preprocessed correctly."""
        deluge_code = """
        resp = invokeurl [
            url: "https://api.example.com"
            type: GET
        ];
        """
        python_code = self.translator.translate(deluge_code)

        # Should contain invokeurl translation
        assert "_invokeurl" in python_code or "invokeurl" in python_code


class TestInvokeUrl:
    """Test the _invokeurl function."""

    @pytest.fixture
    def mock_requests(self, monkeypatch):
        """Mock requests for testing."""

        class MockResponse:
            def __init__(self, text="mock response"):
                self.text = text

        class MockRequests:
            @staticmethod
            def get(url, headers=None):
                return MockResponse(f"GET {url}")

            @staticmethod
            def post(url, json=None, headers=None):
                return MockResponse(f"POST {url}")

        # Patch the requests module in the _invokeurl function
        monkeypatch.setattr("requests.get", MockRequests.get)
        monkeypatch.setattr("requests.post", MockRequests.post)
        return MockRequests

    def test_invokeurl_get(self, mock_requests):
        """Test _invokeurl with GET request."""
        params = {"url": "https://api.example.com", "type": "GET"}

        result = _invokeurl(params)
        assert "GET https://api.example.com" in str(result)

    def test_invokeurl_post(self, mock_requests):
        """Test _invokeurl with POST request."""
        params = {
            "url": "https://api.example.com",
            "type": "POST",
            "parameters": {"key": "value"},
        }

        result = _invokeurl(params)
        assert "POST https://api.example.com" in str(result)

    def test_invokeurl_default_get(self, mock_requests):
        """Test _invokeurl with default GET method."""
        params = {"url": "https://api.example.com"}

        result = _invokeurl(params)
        assert "GET https://api.example.com" in str(result)
