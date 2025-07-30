"""Tests for invokeurl body parameter serialization."""

from deluge_compat import run_deluge_script


class TestInvokeUrlBodySerialization:
    """Test invokeurl body parameter handling."""

    def test_map_body_serialization(self):
        """Test that Map objects are properly serialized in invokeurl body."""
        script = """
        test_data = Map();
        test_data.put("message", "test message");
        test_data.put("conv_id", "test_123");
        test_data.put("number", 42);

        apiResponse = invokeurl
        [
            url :"https://httpbin.org/post"
            type :POST
            body:test_data
            headers:{"Content-Type":"application/json"}
        ];

        return apiResponse;
        """

        result = run_deluge_script(script)
        response_text = str(result)

        # httpbin.org echoes back the JSON we sent
        assert '"message": "test message"' in response_text
        assert '"conv_id": "test_123"' in response_text
        assert '"number": 42' in response_text

    def test_empty_body_handling(self):
        """Test invokeurl with empty or missing body."""
        script = """
        apiResponse = invokeurl
        [
            url :"https://httpbin.org/post"
            type :POST
            headers:{"Content-Type":"application/json"}
        ];

        return apiResponse;
        """

        result = run_deluge_script(script)
        response_text = str(result)

        # Should work without errors
        assert "httpbin.org" in response_text

    def test_string_body_handling(self):
        """Test invokeurl with string body (should be quoted)."""
        script = """
        apiResponse = invokeurl
        [
            url :"https://httpbin.org/post"
            type :POST
            body:"direct string body"
            headers:{"Content-Type":"application/json"}
        ];

        return apiResponse;
        """

        result = run_deluge_script(script)
        response_text = str(result)

        # httpbin.org should receive the string
        assert '"direct string body"' in response_text

    def test_nested_map_body_serialization(self):
        """Test that nested Map objects are properly serialized."""
        script = """
        inner_map = Map();
        inner_map.put("nested_key", "nested_value");

        test_data = Map();
        test_data.put("message", "test message");
        test_data.put("nested", inner_map);

        apiResponse = invokeurl
        [
            url :"https://httpbin.org/post"
            type :POST
            body:test_data
            headers:{"Content-Type":"application/json"}
        ];

        return apiResponse;
        """

        result = run_deluge_script(script)
        response_text = str(result)

        # Check that nested structure is preserved
        assert '"message": "test message"' in response_text
        assert '"nested"' in response_text
        assert '"nested_key": "nested_value"' in response_text
