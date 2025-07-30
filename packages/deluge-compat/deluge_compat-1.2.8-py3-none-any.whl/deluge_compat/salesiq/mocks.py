"""Mock system for SalesIQ objects and API responses."""

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

try:
    from faker import Faker

    HAS_FAKER = True
except ImportError:
    HAS_FAKER = False
    Faker = None  # type: ignore


class VisitorMockSource:
    """Mock data source for visitor objects."""

    def __init__(self, source_type: str = "faker", **config):
        """
        Initialize visitor mock source.

        Args:
            source_type: 'faker', 'json', 'endpoint', or 'none'
            **config: Configuration options for the mock source
        """
        self.source_type = source_type
        self.config = config

        if source_type == "faker" and not HAS_FAKER:
            raise ImportError(
                "faker library is required for 'faker' mock source. Install with: pip install faker"
            )

        if source_type == "faker" and HAS_FAKER and Faker is not None:
            locale = config.get("faker_locale", "en_US")
            seed = config.get("faker_seed")
            self.faker = Faker(locale)
            if seed:
                Faker.seed(seed)

    def get_visitor_data(self, scenario: str | None = None) -> dict[str, Any]:
        """
        Generate visitor data based on the configured source.

        Args:
            scenario: Optional scenario name for JSON sources

        Returns:
            Dictionary containing visitor data
        """
        if self.source_type == "faker":
            return self._generate_faker_data()
        elif self.source_type == "json":
            return self._load_json_data(scenario)
        elif self.source_type == "endpoint":
            return self._fetch_endpoint_data()
        elif self.source_type == "none":
            return {}
        else:
            raise ValueError(f"Unknown visitor mock source type: {self.source_type}")

    def _generate_faker_data(self) -> dict[str, Any]:
        """Generate realistic visitor data using faker."""
        fake = self.faker

        # Generate basic visitor info
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        email = fake.email()

        # Generate conversation ID
        conv_id = f"conv_{fake.random_int(100000, 999999)}"

        return {
            # Basic information
            "name": full_name,
            "email": email,
            "phone": fake.phone_number(),
            "active_conversation_id": conv_id,
            # Visitor context
            "channel": random.choice(
                ["Website", "Facebook", "Instagram", "WhatsApp", "Mobile App"]
            ),
            "browser": fake.user_agent().split()[0],
            "country": fake.country(),
            "country_code": fake.country_code(),
            "time_zone": str(fake.timezone()),
            "language": fake.language_code(),
            "os": fake.user_agent().split()[-1] if "(" in fake.user_agent() else "Unknown",
            "city": fake.city(),
            "state": fake.state(),
            # Page and navigation
            "current_page_url": fake.url(),
            "current_page_title": fake.catch_phrase(),
            "landing_page_url": fake.url(),
            "landing_page_title": fake.catch_phrase(),
            "previous_page_url": fake.url(),
            # Campaign tracking
            "campaign_content": fake.word(),
            "campaign_medium": random.choice(["email", "social", "search", "display"]),
            "campaign_source": random.choice(["google", "facebook", "twitter", "newsletter"]),
            "referer": fake.url(),
            # Additional metadata
            "ip": fake.ipv4(),
            "lead_score": str(fake.random_int(0, 100)),
            "number_of_past_chats": str(fake.random_int(0, 20)),
            "number_of_past_visits": str(fake.random_int(1, 50)),
            "last_visit_time": fake.date_time(tzinfo=timezone.utc).isoformat(),
            # Company information
            "company_name": fake.company(),
            "company_employees": str(fake.random_int(1, 10000)),
            # Unique identifiers
            "visitid": fake.uuid4(),
            "uuid": fake.uuid4(),
            "department_id": str(fake.random_int(1, 10)),
            # Custom fields
            "custom_info": {
                "source": "mock_faker",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    def _load_json_data(self, scenario: str | None = None) -> dict[str, Any]:
        """Load visitor data from JSON file."""
        json_file = self.config.get("mock_file", "mock_visitor.json")
        file_path = Path(json_file)

        if not file_path.exists():
            raise FileNotFoundError(f"Mock visitor JSON file not found: {json_file}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # If scenarios are defined and a scenario is requested
        if scenario and "scenarios" in data and scenario in data["scenarios"]:
            # Merge default data with scenario-specific data
            result = data.get("default", {}).copy()
            result.update(data["scenarios"][scenario])
            return result

        # Return default data
        return data.get("default", data)

    def _fetch_endpoint_data(self) -> dict[str, Any]:
        """Fetch visitor data from endpoint."""
        endpoint = self.config.get("mock_endpoint")
        if not endpoint:
            raise ValueError("mock_endpoint must be specified for endpoint source type")

        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch visitor data from endpoint: {e}") from e


class MessageMockSource:
    """Mock data source for message objects."""

    def __init__(self, source_type: str = "interactive", **config):
        """
        Initialize message mock source.

        Args:
            source_type: 'interactive', 'json', 'endpoint'
            **config: Configuration options
        """
        self.source_type = source_type
        self.config = config
        self._message_index = 0
        self._messages = []

        if source_type == "json":
            self._load_messages_from_json()

    def get_next_message(self) -> str:
        """Get the next message based on source type."""
        if self.source_type == "interactive":
            return self._get_user_input()
        elif self.source_type == "json":
            return self._get_next_from_json()
        elif self.source_type == "endpoint":
            return self._fetch_from_endpoint()
        else:
            raise ValueError(f"Unknown message mock source type: {self.source_type}")

    def _get_user_input(self) -> str:
        """Get message from user input."""
        try:
            return input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            return "end chat"

    def _load_messages_from_json(self) -> None:
        """Load messages from JSON file."""
        json_file = self.config.get("mock_file", "mock_messages.json")
        file_path = Path(json_file)

        if not file_path.exists():
            raise FileNotFoundError(f"Mock messages JSON file not found: {json_file}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        self._messages = data.get("messages", [])

    def _get_next_from_json(self) -> str:
        """Get next message from loaded JSON data."""
        if self._message_index >= len(self._messages):
            return "end chat"  # End conversation when messages are exhausted

        message = self._messages[self._message_index]
        self._message_index += 1
        return message

    def _fetch_from_endpoint(self) -> str:
        """Fetch next message from endpoint."""
        endpoint = self.config.get("mock_endpoint")
        if not endpoint:
            raise ValueError("mock_endpoint must be specified for endpoint source type")

        try:
            response = requests.get(f"{endpoint}?index={self._message_index}", timeout=10)
            response.raise_for_status()
            data = response.json()
            self._message_index += 1
            return data.get("message", "end chat")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch message from endpoint: {e}") from e


class APIMockSource:
    """Mock data source for API responses."""

    def __init__(self, source_type: str = "passthrough", **config):
        """
        Initialize API mock source.

        Args:
            source_type: 'json', 'endpoint', 'passthrough'
            **config: Configuration options
        """
        self.source_type = source_type
        self.config = config
        self._responses = {}

        if source_type == "json":
            try:
                self._load_responses_from_json()
            except FileNotFoundError:
                # Use empty responses if file not found
                self._responses = {}

    def mock_request(self, url: str, method: str, body: Any = None) -> dict[str, Any]:
        """
        Mock an API request based on the configured source.

        Args:
            url: Request URL
            method: HTTP method
            body: Request body

        Returns:
            Mocked response data
        """
        if self.source_type == "json":
            return self._get_json_response(url, body)
        elif self.source_type == "endpoint":
            return self._forward_to_mock_endpoint(url, method, body)
        elif self.source_type == "passthrough":
            return self._make_real_request(url, method, body)
        else:
            raise ValueError(f"Unknown API mock source type: {self.source_type}")

    def _load_responses_from_json(self) -> None:
        """Load API responses from JSON file."""
        json_file = self.config.get("mock_file", "mock_api_responses.json")
        file_path = Path(json_file)

        if not file_path.exists():
            raise FileNotFoundError(f"Mock API responses JSON file not found: {json_file}")

        with open(file_path, encoding="utf-8") as f:
            self._responses = json.load(f)

    def _get_json_response(self, url: str, body: Any) -> dict[str, Any]:
        """Get response from JSON mock data."""
        # Try to find exact URL match
        if url in self._responses:
            response_config = self._responses[url]

            # Check for pattern-based responses
            if "patterns" in response_config and body:
                for pattern in response_config["patterns"]:
                    if self._matches_pattern(pattern.get("request_contains", {}), body):
                        return pattern["response"]

            # Return default response
            return response_config.get("default", {"error": "No mock response configured"})

        # Return generic success response if no mock found
        return {
            "replies": {"text": "Mock response - no specific configuration found"},
            "thread_id": f"mock_thread_{random.randint(1000, 9999)}",
        }

    def _matches_pattern(self, pattern: dict[str, Any], body: Any) -> bool:
        """Check if request body matches a pattern."""
        try:
            body_str = str(body).lower()
            for key, value in pattern.items():
                if key == "message" and isinstance(value, str):
                    import re

                    if not re.search(value.lower(), body_str):
                        return False
            return True
        except Exception:
            return False

    def _forward_to_mock_endpoint(self, url: str, method: str, body: Any) -> dict[str, Any]:
        """Forward request to mock endpoint."""
        mock_endpoint = self.config.get("mock_endpoint")
        if not mock_endpoint:
            raise ValueError("mock_endpoint must be specified for endpoint source type")

        try:
            response = requests.post(
                mock_endpoint,
                json={"original_url": url, "method": method, "body": body},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to forward request to mock endpoint: {e}") from e

    def _make_real_request(self, url: str, method: str, body: Any) -> dict[str, Any]:
        """Make real HTTP request (passthrough mode)."""
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=body, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Return error response compatible with the expected format
            return {
                "error": str(e),
                "replies": {"text": "Sorry, I encountered an error processing your request."},
                "thread_id": None,
            }


class MockManager:
    """Central manager for all mock sources."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize mock manager with configuration.

        Args:
            config: Configuration dictionary for all mock sources
        """
        self.config = config or {}

        # Initialize mock sources
        visitor_config = self.config.get("visitor", {})
        self.visitor_mock = VisitorMockSource(
            source_type=visitor_config.get("mock_source", "faker"), **visitor_config
        )

        message_config = self.config.get("message", {})
        self.message_mock = MessageMockSource(
            source_type=message_config.get("mock_source", "interactive"), **message_config
        )

        api_config = self.config.get("api_responses", {})
        self.api_mock = APIMockSource(
            source_type=api_config.get("mock_source", "passthrough"), **api_config
        )

    def get_visitor(self, scenario: str | None = None):
        """Get a visitor object with mock data."""
        from .core import Visitor

        visitor_data = self.visitor_mock.get_visitor_data(scenario)
        return Visitor(visitor_data)

    def get_message(self) -> str:
        """Get next message from mock source."""
        return self.message_mock.get_next_message()

    def mock_api_call(self, url: str, method: str = "POST", body: Any = None) -> dict[str, Any]:
        """Mock an API call."""
        return self.api_mock.mock_request(url, method, body)
