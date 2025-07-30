"""Tests for edge cases from GitHub issue #2."""

from deluge_compat import run_deluge_script


class TestEdgeCases:
    """Test edge cases that were causing production script failures."""

    def test_map_string_concatenation_in_invokeurl(self):
        """Test Map + string concatenation in invokeurl body parameter."""
        script = """
        to_API_data = Map();
        to_API_data.put("message", "test");
        to_API_data.put("conv_id", "123");

        apiResponse = invokeurl
        [
            url :"https://httpbin.org/post"
            type :POST
            body:to_API_data + ""
            headers:{"Content-Type":"application/json"}
        ];

        return apiResponse;
        """

        result = run_deluge_script(script)
        response_text = str(result)

        # Verify that the Map was properly serialized to JSON
        assert '"message": "test"' in response_text
        assert '"conv_id": "123"' in response_text

    def test_map_concatenation_operations(self):
        """Test various Map concatenation operations."""
        script = """
        data = Map();
        data.put("key", "value");

        // Test Map + string
        json_with_suffix = data + "_suffix";

        // Test string + Map
        json_with_prefix = "prefix_" + data;

        result = Map();
        result.put("with_suffix", json_with_suffix);
        result.put("with_prefix", json_with_prefix);

        return result;
        """

        result = run_deluge_script(script)

        # Check that concatenation produces JSON strings
        suffix_result = result.get("with_suffix")
        prefix_result = result.get("with_prefix")

        assert '{"key": "value"}_suffix' == str(suffix_result)
        assert 'prefix_{"key": "value"}' == str(prefix_result)

    def test_string_escaping_basic(self):
        """Test basic string escaping and replaceAll functionality."""
        script = """
        msg = "Test quote and backslash";
        msg_escaped = msg.replaceAll("back","BACK");

        return msg_escaped;
        """

        result = run_deluge_script(script)
        assert str(result) == "Test quote and BACKslash"

    def test_complex_string_escaping(self):
        """Test complex string escaping patterns that were causing syntax errors."""
        script = r"""
        msg = "Test backslash escaping";
        msg_escaped = msg.replaceAll("\\","\\\\");

        // Test quote escaping
        quote_msg = "Test quote";
        quote_escaped = quote_msg.replaceAll("\"","\\\"");

        result = Map();
        result.put("backslash", msg_escaped);
        result.put("quote", quote_escaped);
        return result;
        """

        result = run_deluge_script(script)
        assert str(result.get("backslash")) == "Test backslash escaping"
        assert str(result.get("quote")) == "Test quote"

    def test_zoho_json_parsing_syntax(self):
        """Test Zoho-style JSON parsing with getJSON(key) parameters."""
        script = """
        // Mock API response as JSON string
        apiResponse = "{\\"replies\\": {\\"text\\": \\"Hello World\\"}, \\"thread_id\\": \\"12345\\"}";

        // Test the Zoho syntax that should work
        replyText = apiResponse.getJSON("replies").getJSON("text");
        thread_id = apiResponse.getJSON("thread_id");

        // Test missing key handling
        missing = apiResponse.getJSON("nonexistent");

        result = Map();
        result.put("replyText", replyText);
        result.put("thread_id", thread_id);
        result.put("missing", missing);
        return result;
        """

        result = run_deluge_script(script)
        assert str(result.get("replyText")) == "Hello World"
        assert str(result.get("thread_id")) == "12345"
        assert result.get("missing") is None

    def test_zoho_salesiq_visitorsession_functions(self):
        """Test Zoho SalesIQ visitorsession functions."""
        script = """
        // Test setting session data
        session_map = Map();
        session_map.put("threadId", "12345");
        session_map.put("userId", "user123");

        set_response = zoho.salesiq.visitorsession.set("testdomain", session_map, "testconnection");

        // Test getting session data
        get_response = zoho.salesiq.visitorsession.get("testdomain", "threadId", "testconnection");

        result = Map();
        result.put("set_status", set_response.get("status"));
        result.put("stored_keys", set_response.get("stored_keys"));
        result.put("retrieved_data", get_response);

        return result;
        """

        result = run_deluge_script(script)

        # Verify the session functions work correctly
        assert result.get("set_status") == "success"
        stored_keys = result.get("stored_keys")
        assert "threadId" in stored_keys
        assert "userId" in stored_keys

        # Verify data can be retrieved
        retrieved = result.get("retrieved_data")
        assert len(retrieved) > 0  # Should have some data

    def test_zoho_adminuserid_access(self):
        """Test access to zoho.adminuserid."""
        script = """
        admin_email = zoho.adminuserid;

        result = Map();
        result.put("admin_email", admin_email);
        result.put("email_format", admin_email.contains("@"));

        return result;
        """

        result = run_deluge_script(script)

        admin_email = str(result.get("admin_email"))
        assert "@" in admin_email
        assert result.get("email_format") is True

    def test_sendmail_functionality(self):
        """Test sendmail block syntax translation and execution."""
        script = """
        // Test sendmail with various parameter types
        session_map = Map();
        session_map.put("threadId", "test123");

        sendmail[
            from :zoho.adminuserid
            to :"admin@examplelab.com"
            subject :"Web Chat Executed"
            message :"<div>Test content</div>"
        ];

        result = Map();
        result.put("admin_email", zoho.adminuserid);
        result.put("session_data", session_map);
        return result;
        """

        result = run_deluge_script(script)

        # Verify sendmail executed successfully and other operations work
        assert "@" in str(result.get("admin_email"))
        assert result.get("session_data").get("threadId") == "test123"

    def test_complex_production_scenario(self):
        """Test a complex scenario combining multiple edge cases."""
        script = """
        // Create API data
        api_data = Map();
        api_data.put("message", "Production test");
        api_data.put("timestamp", "2025-01-01");

        // Store in session
        session_data = Map();
        session_data.put("api_call_data", api_data);
        session_data.put("admin", zoho.adminuserid);

        store_result = zoho.salesiq.visitorsession.set("production", session_data, "main");

        // Retrieve and use in API call (simulated)
        retrieved = zoho.salesiq.visitorsession.get("production", "api_call_data", "main");

        // Simulate JSON serialization that would be sent to API
        json_data = api_data + "";

        result = Map();
        result.put("session_stored", store_result.get("status"));
        result.put("json_serialized", json_data.contains("Production test"));
        result.put("admin_available", session_data.get("admin").contains("@"));

        return result;
        """

        result = run_deluge_script(script)

        # Verify all components work together
        assert result.get("session_stored") == "success"
        assert result.get("json_serialized") is True
        assert result.get("admin_available") is True
