"""Tests for SalesIQ functionality."""

import json
from unittest.mock import Mock, patch

from deluge_compat import Map, deluge_string
from deluge_compat.functions import sendmail
from deluge_compat.salesiq.core import Message, Visitor
from deluge_compat.salesiq.functions import (
    _session_storage,
    visitorsession_get,
    visitorsession_set,
)
from deluge_compat.salesiq.mocks import (
    APIMockSource,
    MessageMockSource,
    MockManager,
    VisitorMockSource,
)


class TestVisitorObject:
    """Test Visitor object functionality."""

    def test_visitor_creation_with_default_data(self):
        """Test Visitor object creation with default data."""
        visitor = Visitor()

        # Check that default data is populated
        assert visitor.getJSON("name") is not None
        assert visitor.getJSON("email") is not None
        assert visitor.getJSON("phone") is not None
        assert visitor.getJSON("active_conversation_id") is not None

    def test_visitor_creation_with_custom_data(self):
        """Test Visitor object creation with custom data."""
        custom_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-0123",
            "state": "California",
        }

        visitor = Visitor(custom_data)

        assert visitor.getJSON("name") == deluge_string("John Doe")
        assert visitor.getJSON("email") == deluge_string("john@example.com")
        assert visitor.getJSON("phone") == deluge_string("+1-555-0123")
        assert visitor.getJSON("state") == deluge_string("California")

    def test_visitor_getjson_returns_deluge_string(self):
        """Test that getJSON returns DelugeString for string values."""
        visitor = Visitor({"name": "Test User"})
        result = visitor.getJSON("name")

        assert isinstance(result, type(deluge_string("")))
        assert str(result) == "Test User"

    def test_visitor_getjson_returns_none_for_missing_key(self):
        """Test that getJSON returns None for missing keys."""
        visitor = Visitor({})
        result = visitor.getJSON("nonexistent_key")

        assert result is None

    def test_visitor_getjson_with_non_string_values(self):
        """Test that getJSON handles non-string values correctly."""
        visitor = Visitor(
            {
                "visit_count": 5,
                "is_vip": True,
                "metadata": {"key": "value"},
            }
        )

        assert visitor.getJSON("visit_count") == 5
        assert visitor.getJSON("is_vip") is True
        assert visitor.getJSON("metadata") == {"key": "value"}


class TestMessageObject:
    """Test Message object functionality."""

    def test_message_creation(self):
        """Test Message object creation."""
        message = Message("Hello, world!")

        assert message.get("text") == deluge_string("Hello, world!")

    def test_message_get_returns_deluge_string(self):
        """Test that Message.get returns DelugeString."""
        message = Message("Test message")
        result = message.get("text")

        assert isinstance(result, type(deluge_string("")))
        assert str(result) == "Test message"

    def test_message_get_with_different_key(self):
        """Test Message.get with different key returns None."""
        message = Message("Test")
        result = message.get("nonexistent")

        assert result is None


class TestVisitorSessionFunctions:
    """Test visitor session management functions."""

    def setup_method(self):
        """Clear session storage before each test."""
        _session_storage.clear()

    def test_visitorsession_set_and_get(self):
        """Test storing and retrieving session data."""
        # Store session data
        session_data = Map()
        session_data.put("user_interest", "products")
        session_data.put("quote_requested", True)

        visitorsession_set("test_portal", session_data, "test_connection")

        # Retrieve session data
        result = visitorsession_get("test_portal", "user_interest", "test_connection")

        assert len(result) > 0
        assert result.get("user_interest_response") == "products"

        data_map = result.get("data")
        assert data_map.get("user_interest") == "products"

    def test_visitorsession_get_nonexistent_key(self):
        """Test retrieving non-existent session data."""
        result = visitorsession_get("test_portal", "nonexistent", "test_connection")

        assert len(result) == 0

    def test_visitorsession_multiple_keys(self):
        """Test storing and retrieving multiple session keys."""
        session_data = Map()
        session_data.put("step", "product_selection")
        session_data.put("category", "software")

        visitorsession_set("portal", session_data, "conn")

        # Get first key
        step_result = visitorsession_get("portal", "step", "conn")
        assert step_result.get("step_response") == "product_selection"

        # Get second key
        category_result = visitorsession_get("portal", "category", "conn")
        assert category_result.get("category_response") == "software"

    def test_visitorsession_overwrite_data(self):
        """Test overwriting existing session data."""
        # Set initial data
        session_data1 = Map()
        session_data1.put("status", "initial")
        visitorsession_set("portal", session_data1, "conn")

        # Overwrite with new data
        session_data2 = Map()
        session_data2.put("status", "updated")
        session_data2.put("new_field", "value")
        visitorsession_set("portal", session_data2, "conn")

        # Verify old data is replaced
        result = visitorsession_get("portal", "status", "conn")
        assert result.get("status_response") == "updated"

        # Verify new field exists
        new_result = visitorsession_get("portal", "new_field", "conn")
        assert new_result.get("new_field_response") == "value"


class TestSendmailFunction:
    """Test sendmail function."""

    def test_sendmail_basic(self):
        """Test basic sendmail functionality."""
        result = sendmail(
            **{"from": "test@example.com"},
            **{"to": "admin@example.com"},
            **{"subject": "Test Email"},
            **{"message": "Hello World"},
        )

        # Verify email data is returned
        assert result.get("status") == "email_sent"
        assert result.get("from") == "test@example.com"
        assert result.get("to") == "admin@example.com"
        assert result.get("subject") == "Test Email"
        assert result.get("message") == "Hello World"

    def test_sendmail_with_variables(self):
        """Test sendmail with variable interpolation."""
        visitor_email = "visitor@example.com"
        message_text = "Help request"

        result = sendmail(
            **{"from": "bot@company.com"},
            **{"to": "support@company.com"},
            **{"subject": "New Inquiry"},
            **{"message": f"From: {visitor_email}, Message: {message_text}"},
        )

        assert result.get("from") == "bot@company.com"
        assert result.get("to") == "support@company.com"
        assert f"From: {visitor_email}, Message: {message_text}" in result.get("message")


class TestVisitorMockSource:
    """Test VisitorMockSource functionality."""

    def test_faker_mock_source(self):
        """Test faker-based visitor mock source."""
        mock_source = VisitorMockSource("faker")
        visitor_data = mock_source.get_visitor_data()

        # Check that required fields are present
        assert "name" in visitor_data
        assert "email" in visitor_data
        assert "phone" in visitor_data
        assert "active_conversation_id" in visitor_data
        assert visitor_data["name"]  # Not empty

    def test_json_mock_source_with_default(self, tmp_path):
        """Test JSON-based visitor mock source with default scenario."""
        # Create test JSON file
        test_data = {
            "default": {
                "name": "Test User",
                "email": "test@example.com",
                "phone": "+1-555-0123",
            }
        }

        json_file = tmp_path / "visitor_test.json"
        json_file.write_text(json.dumps(test_data))

        mock_source = VisitorMockSource("json", mock_file=str(json_file))
        visitor_data = mock_source.get_visitor_data()

        assert visitor_data["name"] == "Test User"
        assert visitor_data["email"] == "test@example.com"
        assert visitor_data["phone"] == "+1-555-0123"

    def test_json_mock_source_with_scenario(self, tmp_path):
        """Test JSON-based visitor mock source with specific scenario."""
        test_data = {
            "default": {
                "name": "Default User",
                "email": "default@example.com",
            },
            "scenarios": {
                "vip_customer": {
                    "name": "VIP User",
                    "email": "vip@example.com",
                    "number_of_past_visits": "10",
                }
            },
        }

        json_file = tmp_path / "visitor_test.json"
        json_file.write_text(json.dumps(test_data))

        mock_source = VisitorMockSource("json", mock_file=str(json_file))
        visitor_data = mock_source.get_visitor_data(scenario="vip_customer")

        assert visitor_data["name"] == "VIP User"
        assert visitor_data["email"] == "vip@example.com"
        assert visitor_data["number_of_past_visits"] == "10"

    def test_endpoint_mock_source(self):
        """Test endpoint-based visitor mock source."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "name": "API User",
                "email": "api@example.com",
            }
            mock_get.return_value = mock_response

            mock_source = VisitorMockSource("endpoint", mock_endpoint="http://test.com/visitor")
            visitor_data = mock_source.get_visitor_data()

            assert visitor_data["name"] == "API User"
            assert visitor_data["email"] == "api@example.com"
            # Check that get was called with the expected URL and timeout
            mock_get.assert_called_once_with("http://test.com/visitor", timeout=10)


class TestMessageMockSource:
    """Test MessageMockSource functionality."""

    def test_json_message_source(self, tmp_path):
        """Test JSON-based message mock source."""
        test_data = {
            "messages": [
                "Hello",
                "How can I help?",
                "Thank you",
            ]
        }

        json_file = tmp_path / "messages_test.json"
        json_file.write_text(json.dumps(test_data))

        mock_source = MessageMockSource("json", mock_file=str(json_file))

        # Get messages in order
        assert mock_source.get_next_message() == "Hello"
        assert mock_source.get_next_message() == "How can I help?"
        assert mock_source.get_next_message() == "Thank you"

        # Should return "end chat" after exhausting messages
        assert mock_source.get_next_message() == "end chat"

    def test_endpoint_message_source(self):
        """Test endpoint-based message mock source."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"message": "API message"}
            mock_get.return_value = mock_response

            mock_source = MessageMockSource("endpoint", mock_endpoint="http://test.com/message")
            message = mock_source.get_next_message()

            assert message == "API message"
            # Check that get was called with the expected base URL
            assert mock_get.called
            call_args = mock_get.call_args[0][0]
            assert "http://test.com/message" in call_args


class TestAPIMockSource:
    """Test APIMockSource functionality."""

    def test_json_api_mock_source(self, tmp_path):
        """Test JSON-based API mock source."""
        test_data = {
            "https://api.example.com/chat": {
                "default": {
                    "replies": {"text": "Default response"},
                    "thread_id": "thread_123",
                },
                "patterns": [
                    {
                        "request_contains": {"message": ".*hello.*"},
                        "response": {
                            "replies": {"text": "Hello there!"},
                        },
                    }
                ],
            }
        }

        json_file = tmp_path / "api_test.json"
        json_file.write_text(json.dumps(test_data))

        mock_source = APIMockSource("json", mock_file=str(json_file))

        # Test default response
        response = mock_source.mock_request("https://api.example.com/chat", "POST", {})
        assert response["replies"]["text"] == "Default response"
        assert response["thread_id"] == "thread_123"

        # Test pattern matching
        request_data = {"message": "hello world"}
        response = mock_source.mock_request("https://api.example.com/chat", "POST", request_data)
        assert response["replies"]["text"] == "Hello there!"

    def test_api_mock_source_unknown_url(self, tmp_path):
        """Test API mock source with unknown URL."""
        json_file = tmp_path / "api_test.json"
        json_file.write_text("{}")

        mock_source = APIMockSource("json", mock_file=str(json_file))
        response = mock_source.mock_request("https://unknown.com", "POST", {})

        # Should return generic response for unknown URLs
        assert "replies" in response
        assert "Mock response" in response["replies"]["text"]


class TestMockManager:
    """Test MockManager functionality."""

    def test_mock_manager_creation(self):
        """Test MockManager creation with default sources."""
        manager = MockManager()

        assert manager.visitor_mock is not None
        assert manager.message_mock is not None
        assert manager.api_mock is not None

    def test_mock_manager_get_visitor(self):
        """Test getting visitor from MockManager."""
        manager = MockManager()
        visitor = manager.get_visitor()

        assert isinstance(visitor, Visitor)
        # Should have some default data
        assert visitor.getJSON("name") is not None

    def test_mock_manager_get_message_interactive(self):
        """Test getting message from MockManager in interactive mode."""
        manager = MockManager()

        with patch("builtins.input", return_value="test message"):
            message = manager.get_message()
            assert message == "test message"

    def test_mock_manager_api_response(self, tmp_path):
        """Test getting API response from MockManager."""
        # Create mock API responses
        test_data = {"https://api.test.com": {"default": {"result": "success"}}}

        json_file = tmp_path / "api_test.json"
        json_file.write_text(json.dumps(test_data))

        manager = MockManager()
        manager.api_mock = APIMockSource("json", mock_file=str(json_file))
        response = manager.api_mock.mock_request("https://api.test.com", "POST", {})

        assert response["result"] == "success"


class TestSalesIQIntegration:
    """Test SalesIQ integration scenarios."""

    def test_complete_visitor_interaction(self):
        """Test a complete visitor interaction scenario."""
        # Create visitor with specific data
        visitor_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "number_of_past_visits": "3",
            "current_page_url": "https://example.com/products",
        }
        visitor = Visitor(visitor_data)

        # Create message
        message = Message("I'm interested in your products")

        # Store session data
        session_data = Map()
        session_data.put("interest", "products")
        visitorsession_set("portal", session_data, "conn")

        # Retrieve and verify
        interest_result = visitorsession_get("portal", "interest", "conn")
        assert interest_result.get("interest_response") == "products"

        # Check visitor data access
        assert str(visitor.getJSON("name")) == "John Doe"
        assert str(visitor.getJSON("current_page_url")) == "https://example.com/products"

        # Check message access
        assert str(message.get("text")) == "I'm interested in your products"

    def test_visitor_vip_scenario(self):
        """Test VIP visitor scenario."""
        visitor_data = {
            "name": "Jane Smith",
            "email": "jane@bigcorp.com",
            "number_of_past_visits": "15",
            "company_name": "Big Corp Inc",
        }
        visitor = Visitor(visitor_data)

        # Simulate VIP check logic
        visits = visitor.getJSON("number_of_past_visits")
        if visits and str(visits).isdigit() and int(str(visits)) > 10:
            vip_status = True
        else:
            vip_status = False

        assert vip_status is True
        assert str(visitor.getJSON("company_name")) == "Big Corp Inc"

    def setup_method(self):
        """Clear session storage before each test."""
        _session_storage.clear()
